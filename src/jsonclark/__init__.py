"""JSON parser with comment support using Lark.

This module provides a Pythonic API similar to the standard json module,
but with support for C-style comments (// and /* */).

Examples:
    >>> import jsonclark
    >>> data = jsonclark.loads('{"name": "Alice"}  // comment')
    >>> data['name']
    'Alice'

    >>> with open('config.json') as f:
    ...     config = jsonclark.load(f)

    >>> data, comments = jsonclark.loads_comments('// Config\\n{"x": 1}')
"""

from jsonclark.parser import (
    JSONDecoder,
    JSONDict,
    JSONList,
    JSONValue,
    extract_comments,
    load,
    load_comments,
    loads,
    loads_comments,
    # Backward compatibility aliases
    load_json_preserving_comments,
    load_json_with_comments,
    JSONWithCommentsParser,
)

__all__ = [
    # Main API (json-like)
    "load",
    "loads",
    "load_comments",
    "loads_comments",
    "extract_comments",
    # Classes
    "JSONDecoder",
    "JSONDict",
    "JSONList",
    "JSONValue",
    # Backward compatibility
    "load_json_with_comments",
    "load_json_preserving_comments",
    "JSONWithCommentsParser",
]

__version__ = "0.1.0"


def hello() -> str:
    return "Hello from jsonclark!"
