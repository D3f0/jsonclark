"""Tests for JSON parser with comment support."""

import pytest
from conftest import (
    COMPLEX_JSON,
    JSON_WITH_BLOCK_COMMENTS,
    JSON_WITH_LINE_COMMENTS,
)

from jsonclark import loads, loads_comments


# Basic JSON parsing tests
@pytest.mark.parser
def test_parse_empty_object():
    """Test parsing an empty object."""
    result = loads("{}")
    assert result == {}


@pytest.mark.parser
def test_parse_empty_array():
    """Test parsing an empty array."""
    result = loads("[]")
    assert result == []


@pytest.mark.parser
def test_parse_simple_object():
    """Test parsing a simple object."""
    json_text = '{"name": "John", "age": 30}'
    result = loads(json_text)
    assert result == {"name": "John", "age": 30}


@pytest.mark.parser
def test_parse_simple_array():
    """Test parsing a simple array."""
    json_text = "[1, 2, 3, 4, 5]"
    result = loads(json_text)
    assert result == [1, 2, 3, 4, 5]


@pytest.mark.parser
def test_parse_nested_structure():
    """Test parsing nested objects and arrays."""
    json_text = '{"users": [{"name": "Alice"}, {"name": "Bob"}]}'
    result = loads(json_text)
    assert result == {"users": [{"name": "Alice"}, {"name": "Bob"}]}


@pytest.mark.parser
def test_parse_string_value():
    """Test parsing a string value."""
    result = loads('"hello world"')
    assert result == "hello world"


@pytest.mark.parser
def test_parse_number_values():
    """Test parsing numeric values."""
    assert loads("42") == 42
    assert loads("3.14") == 3.14
    assert loads("-10") == -10


@pytest.mark.parser
def test_parse_boolean_values():
    """Test parsing boolean values."""
    assert loads("true") is True
    assert loads("false") is False


@pytest.mark.parser
def test_parse_null_value():
    """Test parsing null value."""
    assert loads("null") is None


# Line comment tests
@pytest.mark.parser
def test_parse_line_comment_before_object():
    """Test parsing JSON with line comment before the object."""
    result = loads(JSON_WITH_LINE_COMMENTS)
    assert result == {"name": "Alice", "age": 30}


@pytest.mark.parser
def test_parse_line_comment_inline():
    """Test parsing with inline line comments."""
    json_text = "[1,  // First item\n2,  // Second item\n3]"
    result = loads(json_text)
    assert result == [1, 2, 3]


# Block comment tests
@pytest.mark.parser
def test_parse_block_comment():
    """Test parsing JSON with block comments."""
    result = loads(JSON_WITH_BLOCK_COMMENTS)
    assert result == {"name": "Bob", "age": 25}


@pytest.mark.parser
def test_parse_block_comment_inline():
    """Test parsing with inline block comments."""
    json_text = "[1,  /* First */ 2,  /* Second */ 3]"
    result = loads(json_text)
    assert result == [1, 2, 3]


# Comment preservation tests
@pytest.mark.parser
def test_preserve_single_line_comment():
    """Test that single-line comments are preserved."""
    json_text = '// Configuration comment\n{"name": "John"}'
    result, comments = loads_comments(json_text)
    assert result == {"name": "John"}
    assert "Configuration comment" in comments


@pytest.mark.parser
def test_preserve_multiple_line_comments():
    """Test that multiple line comments are preserved."""
    json_text = '// First\n// Second\n{"x": 1}'
    result, comments = loads_comments(json_text)
    assert result == {"x": 1}
    assert len(comments) == 2
    assert "First" in comments
    assert "Second" in comments


@pytest.mark.parser
def test_preserve_block_comment():
    """Test that block comments are preserved."""
    json_text = '/* Block comment */\n{"x": 1}'
    result, comments = loads_comments(json_text)
    assert result == {"x": 1}
    assert "Block comment" in comments


@pytest.mark.parser
def test_preserve_mixed_comments():
    """Test that mixed comments are preserved."""
    json_text = '// Line\n/* Block */\n{"x": 1}'
    result, comments = loads_comments(json_text)
    assert result == {"x": 1}
    assert len(comments) >= 2


# Complex structure tests
@pytest.mark.parser
def test_complex_config_structure():
    """Test a realistic configuration file with comments."""
    result = loads(COMPLEX_JSON)
    assert result["server"]["host"] == "localhost"
    assert result["server"]["port"] == 8080
    assert result["database"]["type"] == "postgresql"
    assert result["database"]["pool_size"] == 20


@pytest.mark.parser
def test_complex_config_comments_preserved():
    """Test that comments are preserved in complex configs."""
    result, comments = loads_comments(COMPLEX_JSON)
    assert result["server"]["port"] == 8080
    assert len(comments) > 0


# Edge cases
@pytest.mark.parser
def test_empty_comments():
    """Test handling of empty comment markers."""
    json_text = "//\n{}"
    result = loads(json_text)
    assert result == {}


@pytest.mark.parser
def test_comment_with_special_characters():
    """Test comments containing special characters."""
    json_text = '// Comment with special chars: @#$%^&*()\n{"x": 1}'
    result = loads(json_text)
    assert result == {"x": 1}


@pytest.mark.parser
def test_escaped_strings():
    """Test that escaped strings are handled correctly."""
    json_text = '{"message": "Hello\\nWorld"}  // comment'
    result = loads(json_text)
    assert result["message"] == "Hello\nWorld"


@pytest.mark.parser
def test_nested_comment_markers_in_line_comment():
    """Test handling of /* */ markers in // comments."""
    json_text = '// This has /* and */ markers\n{"x": 1}'
    result = loads(json_text)
    assert result == {"x": 1}


# Trailing comma tests
@pytest.mark.parser
def test_trailing_comma_in_object():
    """Test parsing an object with a trailing comma."""
    result = loads('{"name": "Alice", "age": 30,}')
    assert result == {"name": "Alice", "age": 30}


@pytest.mark.parser
def test_trailing_comma_in_array():
    """Test parsing an array with a trailing comma."""
    result = loads("[1, 2, 3,]")
    assert result == [1, 2, 3]


@pytest.mark.parser
def test_trailing_comma_nested_object():
    """Test parsing nested objects with trailing commas."""
    json_text = '{"outer": {"inner": "value",},}'
    result = loads(json_text)
    assert result == {"outer": {"inner": "value"}}


@pytest.mark.parser
def test_trailing_comma_nested_array():
    """Test parsing nested arrays with trailing commas."""
    result = loads("[[1, 2,], [3, 4,],]")
    assert result == [[1, 2], [3, 4]]


@pytest.mark.parser
def test_trailing_comma_with_comments():
    """Test trailing comma combined with comments."""
    json_text = '{\n  "key": "value", // comment\n}'
    result = loads(json_text)
    assert result == {"key": "value"}


@pytest.mark.parser
def test_trailing_comma_real_world():
    """Test a real-world config-style object with trailing commas."""
    json_text = """\
{
  "baseURL": "https://example.com/",
  "apiKey": "secret",
}"""
    result = loads(json_text)
    assert result == {"baseURL": "https://example.com/", "apiKey": "secret"}


# Error handling
@pytest.mark.parser
def test_invalid_json_syntax():
    """Test that invalid JSON raises an error."""
    with pytest.raises(Exception):
        loads('{"incomplete":')


@pytest.mark.parser
def test_invalid_json_with_comments():
    """Test that invalid JSON with comments raises an error."""
    with pytest.raises(Exception):
        loads('// Comment\n{"incomplete":')


@pytest.mark.parser
def test_unmatched_braces():
    """Test handling of unmatched braces."""
    with pytest.raises(Exception):
        loads('{"key": "value"')


@pytest.mark.parser
def test_invalid_number_format():
    """Test handling of invalid number formats."""
    with pytest.raises(Exception):
        loads('{"number": 1.2.3}')
