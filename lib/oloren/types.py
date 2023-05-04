from dataclasses import dataclass
from typing import List, Optional, Union, Any

try:
    from py_ts_interfaces import Interface

except ImportError:
    Interface = object


class Type(Interface):
    pass


@dataclass
class Choice(Type):
    """
    Choice: A class for defining a choice input.

    Represents a user input where they can choose one option from a list of choices.

    Args:
        choices (List[str]): A list of available choices.

    Example::

        @olo.register(description="Choose your favorite color.")
        def favorite_color(color=olo.Choice(choices=["Red", "Green", "Blue"])):
            return f"You chose {color}."
    """

    choices: List[str]


@dataclass
class Num(Type):
    """
    Represents a user input where they can provide a number, either floating or integer.

    Args:
        floating (bool): Whether the input should be a floating-point number. Defaults to True.
        min_value (Optional[float]): The minimum allowed value for the input. Defaults to None.
        max_value (Optional[float]): The maximum allowed value for the input. Defaults to None.

    Example::

        @olo.register(description="Calculate the square of a number.")
        def square(number=olo.Num(floating=False)):
            return number * number
    """

    floating: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None


@dataclass
class String(Type):
    """
    String: A class for defining a string input.

    Represents a user input where they can provide a string.

    Args:
        secret (bool): Defaults to False. Whether the input should be rendered as a secure password field.

    Example::

        @olo.register(description="Call OpenAI GPT API")
        def gpt_query(openaikey=olo.String(secret=True), query=olo.String()):
            ...
    """

    secret: bool = False


@dataclass
class Bool(Type):
    """
    Bool: A class for defining a boolean input.

    Represents a user input where they can choose between True or False.

    Args:
        default (bool): The default/initial value for the input. Defaults to False.

    Example::

        @olo.register(description="Check if a number is even or odd.")
        def even_or_odd(number=olo.Num(floating=False), return_even=olo.Bool()):
            return "even" if number % 2 == 0 else "odd" if return_even else not (number % 2 == 0)
    """

    default: bool = False


@dataclass
class File(Type):
    """
    File: A class for defining a file input.

    Represents a user input where they can upload a file. The file will be available in the function as a string path.

    Args:
        allowed_extensions (Optional[List[str]]): A list of allowed file extensions. Defaults to None.

    Example::

        @olo.register(description="Count the number of lines in a text file.")
        def line_counter(file=olo.File(allowed_extensions=[".txt"])):
            with open(file, "r") as f:
                return len(f.readlines())
    """

    allowed_extensions: Optional[List[str]] = None


@dataclass
class Option(Type):
    """
    Option allows you to specify that a type is optional. Pass the type you want to be optional as the first argument.

    If the user doesn't provide a value for the input, the value will be None, so you must handle this in your code.

    Args:
        wrapped (Any): Type to be made optional.
        _type (Optional[str]): The type of the wrapped type. Will be automatically inferred, user specified values will be ignored.

    Example::

        @olo.register()
        def optional_input(optional=olo.Option(olo.Num())):
            if optional is None:
                return "You didn't provide a value for the optional input."
            return f"You provided {optional} for the optional input."
    """

    inner: Union[Choice, Num, File, Bool, String]
    _type: Optional[str] = None


@dataclass
class Ty(Interface):
    name: str
    ty: Union[Choice, Num, File, Bool, String, Option]
    type: str


@dataclass
class Config(Interface):
    name: str
    description: Optional[str]
    args: List[Ty]
    operator: str
    num_outputs: int


NULL_VALUE = "SPECIALNULLVALUEDONOTSETEVER"


# get all subclasses of Type
__all__ = [subclass.__name__ for subclass in Type.__subclasses__()]

if __name__ == "__main__":
    import sys

    path = sys.argv[1]

    with open(path, "r") as f:
        file = f.read()

    with open(path, "w") as f:
        replacement_type = " | ".join([f'"{x}"' for x in __all__])
        _replacement_type = " | ".join([f'"{x}"' for x in __all__ if x != "Option"])
        f.write(
            file.replace("_type: string | null", "_type: " + _replacement_type).replace(
                "type: string", "type: " + replacement_type
            )
            + f'\nexport const nullValue = "{NULL_VALUE}";'
        )
