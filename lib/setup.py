from setuptools import setup, find_packages
import os

path = os.path.join(os.path.dirname(__file__), "../README.md")

with open(path, "r") as file:
    long_description = file.read()

setup(
    name="oloren",
    version="0.0.8",
    packages=find_packages(exclude=("examples", "frontend")),
    python_requires=">=3.6",
    install_requires=["flask", "flask_cors"],
    description="A simple python library for creating Oloren Orchestrator extensions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Docs": "https://oloren-ai.github.io/python-extension-lib",
        "Github": "https://github.com/Oloren-AI/python-extension-lib",
        "Oloren AI": "https://oloren.ai",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    include_package_data=True,
)
