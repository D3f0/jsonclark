"""JSON parser with support for comments using Lark."""

from dataclasses import dataclass, field
from typing import IO, Any, Optional

from lark import Lark, Transformer, v_args

# Lark grammar for JSON with comments
JSON_WITH_COMMENTS_GRAMMAR = r"""
    ?value: object
          | array
          | string
          | number
          | "true"                 -> true
          | "false"                -> false
          | "null"                 -> null

    array  : "[" [value ("," value)* ","?] "]"
    object : "{" [pair ("," pair)* ","?] "}"
    pair   : string ":" value

    string : ESCAPED_STRING

    number : SIGNED_NUMBER

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %import common.C_COMMENT
    %import common.CPP_COMMENT

    %ignore WS
    %ignore C_COMMENT
    %ignore CPP_COMMENT
"""


class JSONList(list):
    """A list subclass that preserves comment metadata without showing it in repr."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._comments_before: list[str] = []
        self._comments_after: list[str] = []
        self._element_comments: dict[int, tuple[list[str], list[str]]] = {}

    def __repr__(self) -> str:
        """Return clean repr that mimics standard list."""
        return list.__repr__(self)

    def __eq__(self, other: Any) -> bool:
        """Compare as standard list."""
        if isinstance(other, list):
            return list.__eq__(self, other)
        return False

    def set_comments_before(self, comments: list[str]) -> None:
        """Set comments that appear before this list."""
        self._comments_before = comments

    def set_comments_after(self, comments: list[str]) -> None:
        """Set comments that appear after this list."""
        self._comments_after = comments

    def set_element_comments(
        self,
        index: int,
        before: Optional[list[str]] = None,
        after: Optional[list[str]] = None,
    ) -> None:
        """Set comments for a specific element."""
        if before is None:
            before = []
        if after is None:
            after = []
        self._element_comments[index] = (before, after)

    def get_comments(self) -> dict[str, Any]:
        """Get all comment metadata for serialization."""
        return {
            "before": self._comments_before,
            "after": self._comments_after,
            "elements": self._element_comments,
        }


class JSONDict(dict):
    """A dict subclass that preserves comment metadata without showing it in repr."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._comments_before: list[str] = []
        self._comments_after: list[str] = []
        self._key_comments: dict[str, tuple[list[str], list[str]]] = {}

    def __repr__(self) -> str:
        """Return clean repr that mimics standard dict."""
        return dict.__repr__(self)

    def __eq__(self, other: Any) -> bool:
        """Compare as standard dict."""
        if isinstance(other, dict):
            return dict.__eq__(self, other)
        return False

    def set_comments_before(self, comments: list[str]) -> None:
        """Set comments that appear before this dict."""
        self._comments_before = comments

    def set_comments_after(self, comments: list[str]) -> None:
        """Set comments that appear after this dict."""
        self._comments_after = comments

    def set_key_comments(
        self,
        key: str,
        before: Optional[list[str]] = None,
        after: Optional[list[str]] = None,
    ) -> None:
        """Set comments for a specific key."""
        if before is None:
            before = []
        if after is None:
            after = []
        self._key_comments[key] = (before, after)

    def get_comments(self) -> dict[str, Any]:
        """Get all comment metadata for serialization."""
        return {
            "before": self._comments_before,
            "after": self._comments_after,
            "keys": self._key_comments,
        }


@dataclass
class JSONValue:
    """Represents a JSON value with optional associated comments."""

    value: Any
    comments_before: list[str] = field(default_factory=list)
    comments_after: list[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"JSONValue(value={self.value!r}, comments_before={self.comments_before}, comments_after={self.comments_after})"


class JSONTransformer(Transformer):
    """Transformer that converts Lark tree to Python objects."""

    @v_args(inline=True)
    def string(self, s: Any) -> str:
        return s.value[1:-1].encode().decode("unicode_escape")

    @v_args(inline=True)
    def number(self, n: Any) -> float | int:
        val = n.value
        return int(val) if "." not in val and "e" not in val.lower() else float(val)

    def array(self, items: list) -> JSONList:
        filtered = [item for item in items if item is not None]
        result = JSONList(filtered)
        return result

    def pair(self, items: list) -> tuple:
        return tuple(items)

    def object(self, items: list) -> JSONDict:
        filtered = [item for item in items if item is not None]
        result = JSONDict(dict(filtered))
        return result

    def true(self, _=None) -> bool:
        return True

    def false(self, _=None) -> bool:
        return False

    def null(self, _=None) -> None:
        return None


class JSONDecoder:
    """Decoder for JSON with comments, similar to json.JSONDecoder."""

    def __init__(self) -> None:
        self.parser = Lark(
            JSON_WITH_COMMENTS_GRAMMAR,
            start="value",
            parser="lalr",
            transformer=JSONTransformer(),
        )
        self._extracted_comments: list[str] = []

    def decode(self, s: str) -> Any:
        """Decode a JSON string, ignoring comments.

        Args:
            s: JSON string possibly containing C-style comments

        Returns:
            Parsed Python object (JSONDict/JSONList/str/number/bool/None)

        Raises:
            lark.exceptions.LarkError: If JSON is invalid
        """
        self._extracted_comments = self._extract_comments(s)
        return self.parser.parse(s)

    def decode_with_comments(self, s: str) -> tuple[Any, list[str]]:
        """Decode JSON and return both value and extracted comments.

        Args:
            s: JSON string possibly containing C-style comments

        Returns:
            Tuple of (parsed_value, comments_list)
        """
        comments = self._extract_comments(s)
        value = self.decode(s)
        return value, comments

    # Backward compatibility methods
    def parse(self, text: str) -> Any:
        """Backward compatibility method. Use decode() instead."""
        return self.decode(text)

    def parse_with_comments(self, text: str) -> dict[str, Any]:
        """Backward compatibility method. Use decode_with_comments() instead."""
        value, comments = self.decode_with_comments(text)
        return {"value": value, "comments": comments}

    @staticmethod
    def _extract_comments(text: str) -> list[str]:
        """Extract all comments from JSON text."""
        comments = []
        i = 0
        while i < len(text):
            if i < len(text) - 1 and text[i : i + 2] == "//":
                end = text.find("\n", i)
                if end == -1:
                    end = len(text)
                comment = text[i + 2 : end].strip()
                if comment:
                    comments.append(comment)
                i = end
            elif i < len(text) - 1 and text[i : i + 2] == "/*":
                end = text.find("*/", i + 2)
                if end != -1:
                    comment = text[i + 2 : end].strip()
                    if comment:
                        comments.append(comment)
                    i = end + 2
                else:
                    i += 1
            else:
                i += 1
        return comments


# Module-level decoder instance (like json module)
_default_decoder = JSONDecoder()


def loads(s: str) -> Any:
    """Deserialize a JSON string with comments to a Python object.

    Similar to json.loads(), but supports C-style comments (// and /* */).

    Args:
        s: JSON string possibly containing comments

    Returns:
        Parsed Python object (JSONDict/JSONList/str/number/bool/None)

    Raises:
        lark.exceptions.LarkError: If JSON is invalid

    Examples:
        >>> data = loads('{\"name\": \"Alice\"}  // comment')
        >>> data['name']
        'Alice'
    """
    return _default_decoder.decode(s)


def load(fp: IO[str]) -> Any:
    """Deserialize a JSON file with comments to a Python object.

    Similar to json.load(), but supports C-style comments (// and /* */).

    Args:
        fp: File-like object containing JSON with possible comments

    Returns:
        Parsed Python object (JSONDict/JSONList/str/number/bool/None)

    Raises:
        lark.exceptions.LarkError: If JSON is invalid

    Examples:
        >>> with open('config.json') as f:
        ...     config = load(f)
    """
    return loads(fp.read())


def loads_comments(s: str) -> tuple[Any, list[str]]:
    """Deserialize JSON with comments, returning value and extracted comments.

    Args:
        s: JSON string possibly containing comments

    Returns:
        Tuple of (parsed_value, comments_list)

    Examples:
        >>> data, comments = loads_comments('// Config\\n{\"x\": 1}')
        >>> data
        {'x': 1}
        >>> comments
        ['Config']
    """
    return _default_decoder.decode_with_comments(s)


def load_comments(fp: IO[str]) -> tuple[Any, list[str]]:
    """Deserialize JSON file with comments, returning value and extracted comments.

    Args:
        fp: File-like object containing JSON with possible comments

    Returns:
        Tuple of (parsed_value, comments_list)

    Examples:
        >>> with open('config.json') as f:
        ...     config, comments = load_comments(f)
    """
    return loads_comments(fp.read())


def extract_comments(text: str) -> list[str]:
    """Extract all comments from JSON text.

    Args:
        text: JSON string possibly containing comments

    Returns:
        List of comment strings (without the comment delimiters)

    Examples:
        >>> extract_comments('// comment\\n{}')
        ['comment']
    """
    return JSONDecoder._extract_comments(text)


# Convenience aliases for backward compatibility
load_json_with_comments = loads
load_json_preserving_comments = loads_comments
JSONWithCommentsParser = JSONDecoder


# Backward compatibility wrapper for old API
def _old_style_load_json_preserving_comments(s: str) -> dict[str, Any]:
    """Old API wrapper that returns dict with 'value' and 'comments' keys."""
    value, comments = loads_comments(s)
    return {"value": value, "comments": comments}


# Override the alias to use the wrapper
load_json_preserving_comments = _old_style_load_json_preserving_comments
