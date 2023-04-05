import networkx as nx
from matplotlib import pyplot as plt
import warnings

from tree_climber.base_visitor import BaseVisitor
from tree_climber.tree_sitter_utils import c_parser


def assert_boolean_expression(n):
    assert (
        n.type.endswith("_statement")
        or n.type.endswith("_expression")
        or n.type in ("true", "false", "identifier", "number_literal")  # TODO: handle ERROR (most often shows up as comma_expression in for loop onditioanl)
    ), (n, n.type, n.text.decode())


def assert_branch_target(n):
    assert (
        n.type.endswith("_statement")
        or n.type.endswith("_expression")
        or n.type in ("else",)
    ), (n, n.type)
    

def check_ast_error_in_children(n):
    if any(c.type == "ERROR" for c in n.children):
        raise AstErrorException()


class AstErrorException(Exception):
    pass


class ASTCreator(BaseVisitor):
    """
    AST visitor which creates a CFG.
    After traversing the AST by calling visit() on the root, self.cfg has a complete CFG.
    """

    def __init__(self, strict):
        super(ASTCreator).__init__()
        self.ast = nx.DiGraph()
        self.node_id = 0
        self.strict = strict

    @staticmethod
    def make_ast(root_node, strict=True):
        visitor = ASTCreator(strict=strict)
        visitor.visit(root_node, parent_id=None)
        return visitor.ast

    def visit(self, n, **kwargs):
        if n.type == "ERROR" and self.strict:
            raise AstErrorException()
        else:
            warnings.warn("encountered ERROR in AST")

        super().visit(n, **kwargs)

    def visit_for_statement(self, n, **kwargs):
        self.visit_default(
            n, has_init=True, has_cond=True, has_incr=True, **kwargs
        )

    def visit_case_statement(self, n, **kwargs):
        children = n.children
        check_ast_error_in_children(n)
        label_end = 0
        while children[label_end].type != ":":
            label_end += 1
        label_end -= 1
        body_begin = label_end + 2
        is_default = any(c for c in n.children if c.text.decode() == "default")
        self.visit_default(n, body_begin=body_begin, is_default=is_default, **kwargs)

    def visit_default(self, n, parent_id, **kwargs):
        code = n.text.decode()
        my_id = self.node_id
        self.node_id += 1
        if parent_id is None:
            self.ast.graph["root_node"] = my_id
        if n.is_named and n.type != "comment":

            def attr_to_label(node_type, code):
                lines = code.splitlines()
                if len(lines) > 0:
                    code = lines[0]
                    max_len = 27
                    trimmed_code = code[:max_len]
                    if len(lines) > 1 or len(code) > max_len:
                        trimmed_code += "..."
                else:
                    trimmed_code = code
                return node_type + "\n" + trimmed_code

            self.ast.add_node(
                my_id,
                n=n,
                label=attr_to_label(n.type, code),
                code=code,
                node_type=n.type,
                start=n.start_point,
                end=n.end_point,
                **kwargs
            )
            if parent_id is not None:
                self.ast.add_edge(parent_id, my_id)
            self.visit_children(n, parent_id=my_id)
            
def test():
    code = """#include <stdio.h>
int main()
{
    int i = 0;
    for (; i < 10; i ++) {
        printf("%d\n", i);
    }
    return 0;
}
"""
    tree = c_parser.parse(bytes(code, "utf8"))
    ast = ASTCreator.make_ast(tree.root_node)
    pos = nx.drawing.nx_agraph.graphviz_layout(ast, prog="dot")
    nx.draw(
        ast,
        pos=pos,
        labels={n: attr["label"] for n, attr in ast.nodes(data=True)},
        with_labels=True,
    )
    plt.show()
