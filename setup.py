from setuptools import setup

setup(
    name="pre-commit-json-replace",
    version="0.1.0",
    description="A pre-commit hook that replaces values for specified keys in JSON files",
    py_modules=["json_replace"],
    install_requires=[
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": ["json-replace=json_replace:main"],
    },
    python_requires=">=3.8",
)
