# Quick Start Guide - jsonclark

## Installation

```bash
pip install jsonclark
```

## Basic Usage

### Parse JSON with Comments

```python
from jsonclark import load_json_with_comments

json_text = """
{
    // This is a comment
    "name": "Alice",
    /* This is a block comment */
    "age": 30
}
"""

result = load_json_with_comments(json_text)
print(result)  # {'name': 'Alice', 'age': 30}
```

### Extract and Preserve Comments

```python
from jsonclark import load_json_preserving_comments

json_text = """
// Configuration
{
    "debug": true  // Enable debugging
}
"""

result = load_json_preserving_comments(json_text)
print(result["value"])      # {'debug': True}
print(result["comments"])   # ['Configuration', 'Enable debugging']
```

## Supported Comment Types

### Line Comments (C++ style)
```json
{
    // Single line comment
    "key": "value"
}
```

### Block Comments (C style)
```json
{
    /* 
     * Multi-line comment
     */
    "key": "value"
}
```

## Common Patterns

### Configuration Files
```python
config = load_json_with_comments("""
{
    // Server settings
    "server": {
        "port": 8080,  // HTTP port
        "host": "localhost"  // Bind address
    }
}
""")
```

### API Schemas
```python
schema = load_json_with_comments("""
{
    // API v1 schema
    "endpoints": [
        {
            "path": "/api/users",  // Get all users
            "method": "GET"
        }
    ]
}
""")
```

## API Reference

### Functions

**`load_json_with_comments(text: str) -> Any`**
- Parses JSON with comments
- Returns the parsed Python object
- Ignores all comments

**`load_json_preserving_comments(text: str) -> dict[str, Any]`**
- Parses JSON with comments
- Returns `{"value": object, "comments": [list]}`
- Preserves extracted comments

### Classes

**`JSONWithCommentsParser`**
- Main parser class
- Use when you need more control

```python
parser = JSONWithCommentsParser()
result = parser.parse('// comment\n{}')
```

## Testing

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_parser.py

# Run specific test
pytest tests/test_parser.py::TestBasicJSONParsing::test_parse_empty_object
```

## Tips & Tricks

1. **Comments are stripped during parsing** - Use `load_json_preserving_comments()` if you need them
2. **Comments can appear anywhere** - Before, after, or between JSON elements
3. **Nested comments not supported** - Only single-level comment nesting
4. **Unicode in comments works** - Full UTF-8 support for comment text
5. **Standard JSON validation** - All standard JSON rules still apply to data

## Error Handling

```python
from jsonclark import load_json_with_comments

try:
    result = load_json_with_comments('// comment\n{invalid}')
except Exception as e:
    print(f"Parse error: {e}")
```

## Examples

See `examples/demo.py` for comprehensive examples including:
- Line comments
- Block comments
- Mixed comment types
- Complex nested structures
- Comment preservation

Run the demo:
```bash
python examples/demo.py
```

## See Also

- [README.md](README.md) - Full documentation
- [examples/demo.py](examples/demo.py) - Working examples
- [tests/test_parser.py](tests/test_parser.py) - Extensive test examples
