from setuptools import setup, find_packages

setup(
    name="oloren",
    version="0.0.3",
    packages=find_packages(exclude=("examples", "frontend")),
    python_requires=">=3.6",
    install_requires=[
        "flask",
    ],
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
