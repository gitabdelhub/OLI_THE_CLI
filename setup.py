from setuptools import setup, find_packages

setup(
    name="oli-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.12.0",
        "rich>=13.0.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "oli = oli_cli.main:app",
        ],
    },
)
