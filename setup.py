from setuptools import find_packages, setup

__version__ = "0.0.1"


with open("README.md") as description_file:
    readme = description_file.read()

with open("requirements.txt") as requirements_file:
    requirements = [line for line in requirements_file]

setup(
    name="tree-climber",
    version=__version__,
    author="data-engineering-trybe",
    python_requires=">=3.8.5",
    description="A framework to modularize and facilitate ETLs.",
    long_description=readme,
    url="https://github.com/betrybe/tree-climber",
    install_requires=requirements,
    packages=find_packages(),
)