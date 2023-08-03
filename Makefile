## Requirements

.PHONY: requirements-test
requirements-test:
	@PYTHONPATH=. python -m pip install -r requirements.test.txt

.PHONY: requirements-lint
requirements-lint:
	@PYTHONPATH=. python -m pip install -r requirements.lint.txt

.PHONY: minimum-requirements
minimum-requirements:
	@PYTHONPATH=. python -m pip install -U -r requirements.txt

.PHONY: dev-requirements
dev-requirements:
	@PYTHONPATH=. python -m pip install -U -r requirements.dev.txt

.PHONY: requirements
## install all requirements
requirements: requirements-test requirements-lint dev-requirements minimum-requirements

## Style Checks

.PHONY: style-check
style-check:
	@echo ""
	@echo "Code Style"
	@echo "=========="
	@echo ""
	@python -m black --check -t py38 --exclude="build/|buck-out/|dist/|_build/|pip/|\.pip/|\.git/|\.hg/|\.mypy_cache/|\.tox/|\.venv/" . && echo "\n\nSuccess" || (echo "\n\nFailure\n\nRun \"make black\" to apply style formatting to your code"; return 2)
	@echo ""

.PHONY: check-flake8
check-flake8:
	@echo ""
	@echo "Flake 8"
	@echo "======="
	@echo ""
	@-python -m flake8 climber/ && echo "climber module success"
	@-python -m flake8 tests/ && echo "tests module success"
	@echo ""

.PHONY: checks
checks:
	@echo ""
	@echo "Code Style & Flake 8"
	@echo "--------------------"
	@echo ""
	@make style-check
	@make check-flake8
	@echo ""

.PHONY: black
black:
	@python -m black -t py38 --exclude="build/|buck-out/|dist/|_build/|pip/|\.pip/|\.git/|\.hg/|\.mypy_cache/|\.tox/|\.venv/" .

## Tests

.PHONY: tests
tests:
	@python -m pytest --cov-branch --cov-report term-missing --cov=climber tests/

## Build wheel

.PHONY: build
build:
	@PYTHONPATH=. python -m setup sdist bdist_wheel

## Clean Data

.PHONY: clean
clean:
	@find ./ -type d -name 'htmlcov' -exec rm -rf {} +;
	@find ./ -type d -name 'coverage.xml' -exec rm -rf {} +;
	@find ./ -type f -name 'coverage-badge.svg' -exec rm -f {} \;
	@find ./ -type f -name '.coverage' -exec rm -f {} \;
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;