"""Tests for Pythonic API similar to json module."""

import pytest
import io
from jsonclark import load, loads, load_comments, loads_comments, extract_comments


# loads() string parsing tests
@pytest.mark.parser
def test_loads_simple_object():
    """Test loading a simple object."""
    result = loads('{"name": "Alice", "age": 30}')
    assert result == {"name": "Alice", "age": 30}


@pytest.mark.parser
def test_loads_simple_array():
    """Test loading a simple array."""
    result = loads("[1, 2, 3]")
    assert result == [1, 2, 3]


@pytest.mark.parser
def test_loads_string():
    """Test loading a string value."""
    result = loads('"hello world"')
    assert result == "hello world"


@pytest.mark.parser
def test_loads_numbers():
    """Test loading numbers."""
    assert loads("42") == 42
    assert loads("3.14") == 3.14
    assert loads("-10") == -10


@pytest.mark.parser
def test_loads_booleans():
    """Test loading boolean values."""
    assert loads("true") is True
    assert loads("false") is False


@pytest.mark.parser
def test_loads_null():
    """Test loading null value."""
    assert loads("null") is None


@pytest.mark.parser
def test_loads_with_line_comments():
    """Test loads ignores line comments."""
    json_text = '{"name": "Bob", "age": 25}  // comment'
    result = loads(json_text)
    assert result == {"name": "Bob", "age": 25}


@pytest.mark.parser
def test_loads_with_block_comments():
    """Test loads ignores block comments."""
    json_text = '{"name": "Charlie", "age": 35}  /* comment */'
    result = loads(json_text)
    assert result == {"name": "Charlie", "age": 35}


# load() file parsing tests
@pytest.mark.parser
def test_load_from_stringio():
    """Test loading from a file-like object."""
    json_text = '{"key": "value"}'
    fp = io.StringIO(json_text)
    result = load(fp)
    assert result == {"key": "value"}


@pytest.mark.parser
def test_load_with_comments():
    """Test loading file with comments."""
    json_text = '{"debug": true, "port": 8080}  // config'
    fp = io.StringIO(json_text)
    result = load(fp)
    assert result == {"debug": True, "port": 8080}


@pytest.mark.parser
def test_load_complex_structure():
    """Test loading complex nested structure."""
    json_text = (
        '{"server": {"host": "localhost", "port": 3000}, "db": {"type": "postgresql"}}'
    )
    fp = io.StringIO(json_text)
    result = load(fp)
    assert result["server"]["port"] == 3000
    assert result["db"]["type"] == "postgresql"


# loads_comments() tests
@pytest.mark.parser
def test_loads_comments_extracts_comments():
    """Test that loads_comments extracts comments."""
    json_text = '// Configuration\n{"name": "test"}'
    value, comments = loads_comments(json_text)
    assert value == {"name": "test"}
    assert "Configuration" in comments


@pytest.mark.parser
def test_loads_comments_returns_tuple():
    """Test that loads_comments returns (value, comments) tuple."""
    result = loads_comments('{"x": 1}  // comment')
    assert isinstance(result, tuple)
    assert len(result) == 2
    value, comments = result
    assert value == {"x": 1}
    assert isinstance(comments, list)


@pytest.mark.parser
def test_loads_comments_multiple_comments():
    """Test extracting multiple comments."""
    json_text = '// First\n// Second\n{"key": "value"}'
    value, comments = loads_comments(json_text)
    assert value == {"key": "value"}
    assert len(comments) >= 2


# load_comments() tests
@pytest.mark.parser
def test_load_comments_from_file():
    """Test loading file and extracting comments."""
    json_text = '// Configuration file\n{"setting": "value"}'
    fp = io.StringIO(json_text)
    value, comments = load_comments(fp)
    assert value == {"setting": "value"}
    assert "Configuration file" in comments


@pytest.mark.parser
def test_load_comments_returns_tuple():
    """Test that load_comments returns (value, comments) tuple."""
    fp = io.StringIO('{"x": 1}  // comment')
    result = load_comments(fp)
    assert isinstance(result, tuple)
    assert len(result) == 2


# extract_comments() tests
@pytest.mark.parser
def test_extract_comments_line_only():
    """Test extracting only line comments."""
    text = "// Comment 1\n// Comment 2\n{}"
    comments = extract_comments(text)
    assert "Comment 1" in comments
    assert "Comment 2" in comments


@pytest.mark.parser
def test_extract_comments_block_only():
    """Test extracting only block comments."""
    text = "/* Comment 1 */\n/* Comment 2 */\n{}"
    comments = extract_comments(text)
    assert "Comment 1" in comments
    assert "Comment 2" in comments


@pytest.mark.parser
def test_extract_comments_mixed():
    """Test extracting mixed comment types."""
    text = "// Line comment\n/* Block comment */\n{}"
    comments = extract_comments(text)
    assert "Line comment" in comments
    assert "Block comment" in comments


@pytest.mark.parser
def test_extract_comments_no_comments():
    """Test when there are no comments."""
    text = '{"key": "value"}'
    comments = extract_comments(text)
    assert comments == []


# Consistency tests
@pytest.mark.parser
def test_loads_and_load_consistency():
    """Test that loads and load produce identical results."""
    json_text = '{"key": "value"}'
    result_loads = loads(json_text)
    result_load = load(io.StringIO(json_text))
    assert result_loads == result_load


@pytest.mark.parser
def test_loads_comments_and_load_comments_consistency():
    """Test that loads_comments and load_comments are consistent."""
    json_text = "// Comment\n{}"
    value1, comments1 = loads_comments(json_text)
    value2, comments2 = load_comments(io.StringIO(json_text))
    assert value1 == value2
    assert comments1 == comments2


# Error handling tests
@pytest.mark.parser
def test_loads_invalid_json():
    """Test that invalid JSON raises an error."""
    with pytest.raises(Exception):
        loads('{"incomplete":')


@pytest.mark.parser
def test_load_invalid_json():
    """Test that invalid JSON in file raises error."""
    with pytest.raises(Exception):
        load(io.StringIO('{"incomplete":'))


@pytest.mark.parser
def test_loads_comments_invalid_json():
    """Test that loads_comments also raises on invalid JSON."""
    with pytest.raises(Exception):
        loads_comments("[1, 2,")


@pytest.mark.parser
def test_load_comments_invalid_json():
    """Test that load_comments also raises on invalid JSON."""
    with pytest.raises(Exception):
        load_comments(io.StringIO("[1, 2,"))
