# Oloren Orchestrator - Python Extension Library

## Usage

### Installation

```bash
pip install oloren
```

A requirement is that you use Python version > 3.7 as the code uses dataclasses which were introduced in that version.

If for some reason you want to use it with Python 3.6 you can install the backport of dataclasses for Python 3.6 with:

```bash
pip install dataclasses
```

### Getting Started

Check out this minimal example to get started:

```python
import oloren as olo


@olo.register(description="Basic math operations on two numbers.")
def operation(operation=olo.Choice(["Add", "Subtract", "Multiply", "Divide"]), a=olo.Num(), b=olo.Num()):
    if operation == "Add":
        return a + b
    elif operation == "Subtract":
        return a - b
    elif operation == "Multiply":
        return a * b
    elif operation == "Divide":
        return a / b


@olo.register()
def number(num=olo.Num()):
    return num


if __name__ == "__main__":
    olo.run()
```

The key requirements are that each argument of your function has a default value that is set to one of the special
Oloren types. These types subclass their relevant returned data types (e.g. string, int, float) so your autocomplete
will work as normal.

## Contributing

Full contributing docs are a todo, but here are some useful commands to keep in mind when making modifications to this library.

```bash
make types  # build typescript types from types.py
make dev  # start dev frontend server
make build  # build frontend code
make pypi  # push code to pypi
```
