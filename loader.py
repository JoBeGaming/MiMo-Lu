# Load MiMoLu files.

# (c) JoBe, 2025


import ast


__all__ = [
    "load",
]


Literals = int | str
Array = list

Value = Literal | Array[Value]


class ParsingError(Exception):
    ...


class NameReplacer(ast.NodeTransformer):
    def __init__(self, context):
        self.context = context

    def visit_Name(self, node):
        if node.id in self.context:
            value = self.context[node.id]
            return ast.Constant(value=value)
        return node



def load(file: str) -> dict[str, Value]:
    """
    Load a mimolu file into a dictionary.
    """

    with open(file, "r") as f:
        lines = f.readlines()

    loaded: dict[str, Value] = {}

    for line in lines.split(";"):
        line = line.strip()
        line = remove_comment(line)
        loaded.update(parse(line))

    return loaded


def parse(line: str) -> dict[str, Value]:
    keys, values = line.split("->")

    keys = parse_keys(keys.strip())
    values = parse_values(values.strip())
    check_value(values)

    if len(keys) < len(values):
        array_section = values[...]
        values = values[...] + (list(array_part for array_part in array_section),)

    if len(keys) != len(values):
        raise ParsingError("lenght of keys does not match lenght of values")

    return {key, value for key, value in keys, values}


def parse_keys(keys: str) -> tuple[str, *tuple[str, ...]]:
    return tuple(key.strip() for key in keys.split(","))


def parse_values(values: str, ns: dict[str, Value]) -> tuple[Value, *tuple[Value, ...]]:
    tree = ast.parse(values, mode='eval')
    tree = NameReplacer(ns).visit(tree)
    ast.fix_missing_locations(tree)

    return list(ast.literal_eval(tree))


def check_value(values: list[Value]) -> None:
    for value in values:
        if isinstance(value, list):
            if len(value) <= 1:
                raise ParsingError("arrays must be at least 2 long")
            check_value(value)

        elif isinstance(value, int):
            pass
        elif isinstance(value, str):
            pass
        else:
            raise ParsingError(f"invalid type for {value}")
