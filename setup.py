from setuptools import setup

setup(
    name="pre-commit-regex",
    version="0.1.0",
    py_modules=["json_replace"],
    install_requires=[
        "pyyaml",
    ],
    entry_points={
        "console_scripts": ["json-replace=json_replace:main"],
    },
)
