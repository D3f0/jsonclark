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

import subprocess
from importlib.metadata import PackageNotFoundError, version

from jsonclark.parser import (
    JSONDecoder,
    JSONDict,
    JSONList,
    JSONValue,
    JSONWithCommentsParser,
    extract_comments,
    load,
    load_comments,
    # Backward compatibility aliases
    load_json_preserving_comments,
    load_json_with_comments,
    loads,
    loads_comments,
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


def _get_version() -> str:
    """Get version from package metadata or compute dynamically from git tags."""
    # First try to get version from installed package metadata
    try:
        return version("jsonclark")
    except PackageNotFoundError:
        pass

    # If not installed, compute dynamically using uv-dynamic-versioning
    try:
        result = subprocess.run(
            ["uvx", "--with", "uv-dynamic-versioning", "hatchling", "version"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Fallback if all methods fail
    return "0.0.0+unknown"


__version__ = _get_version()


def hello() -> str:
    return "Hello from jsonclark!"
