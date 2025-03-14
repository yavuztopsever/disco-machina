from setuptools import setup, find_packages

setup(
    name="calculator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.8",
    description="A simple calculator library",
    author="Test Author",
    author_email="test@example.com",
    entry_points={
        "console_scripts": [
            "calc=calculator.cli:main",
        ],
    },
)