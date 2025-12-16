# jsonclark - JSON Comments parsed with Lark

This library parses JSON files that contain C-style comments (`//` and `/* */`), 
which is useful commonly used in  configuration files and other applications 
where comments enhance readability. Notable cases are VSCode and Zed editor.

## Features

- Parses JSON with both single-line (`//`) and multi-line (`/* */`) comments.
- Extract and **preserve** comments while parsing
- Full JSON compatibility (objects, arrays, strings, numbers, booleans, null)
- Built with Lark for reliable parsing
- Comprehensive test coverage
- CLI tool with support for yq expressions to modify JSON while preserving comments

## Disclaimer

A big part of this repository has been generated with Code assistants.

## Installation

```bash
pip install jsonclark
```

Or with development dependencies:

```bash
pip install "jsonclark[dev]"
```

## Command-Line Tool

After installing jsonclark, you can use the `jsonclark` command to pretty-print JSON files with support for comments, similar to Python's `json.tool`:

### Usage

```bash
# Pretty-print JSON from stdin
cat config.jsonc | jsonclark

# Pretty-print with custom indentation
cat config.jsonc | jsonclark --indent 4

# Sort keys in output
cat config.jsonc | jsonclark --sort-keys

# Show extracted comments
cat config.jsonc | jsonclark --comments

# Pretty-print from file
jsonclark config.jsonc

# Apply yq expression to modify JSON (preserves comments for file input)
jsonclark --yq '.port = 9000' config.jsonc

# All options together
jsonclark --indent 4 --sort-keys --comments config.jsonc
```

### Options

- `--indent INDENT`: Number of spaces for indentation (default: 2)
- `--sort-keys`: Sort dictionary keys in output
- `--comments`: Show extracted comments in the output
- `--yq EXPRESSION`: Apply a yq expression to modify the JSON. When used with file input, automatically creates a backup (`file.bak`) before modification.
- `--version`: Show program version
- `--help`: Show help message

### Using yq for JSON Modification

The `--yq` flag allows you to apply [yq expressions](https://mikefarah.gitbook.io/yq/) to modify your JSON while preserving comments (when operating on files). This is useful for CI/CD pipelines and configuration management.

#### Requirements

The `yq` binary must be installed. Install it with:

**On macOS:**
```bash
brew install yq
```

**From GitHub releases:**
Visit https://github.com/mikefarah/yq/releases

**Using pip:**
```bash
pip install yq
```

#### Examples

```bash
# Modify a single key
jsonclark --yq '.port = 9000' config.jsonc

# Add a new key
jsonclark --yq '.debug = true' config.jsonc

# Delete a key
jsonclark --yq 'del(.deprecated_field)' config.jsonc

# Modify nested values
jsonclark --yq '.server.host = "0.0.0.0"' config.jsonc

# Work with stdin (output to stdout)
cat config.jsonc | jsonclark --yq '.version = "2.0"'
```

#### Backup on File Modification

When `--yq` is used with file input, jsonclark automatically creates a backup file:

```bash
jsonclark --yq '.port = 9000' config.jsonc
# Creates: config.jsonc.bak (contains the original)
# Updates: config.jsonc (contains the modified version)
```

If yq is not installed, you'll see an error message with installation instructions.



## Quick Start

### Basic Usage

Parse JSON with comments using the `load_json_with_comments()` function:

```python
from jsonclark import load_json_with_comments

json_text = """
{
    // User configuration
    "name": "John Doe",
    // Age in years
    "age": 30
}
"""

config = load_json_with_comments(json_text)
print(config)  # {'name': 'John Doe', 'age': 30}
```

### Preserving Comments

If you want to extract comments separately, use `load_json_preserving_comments()`:

```python
from jsonclark import load_json_preserving_comments

json_text = """
// Configuration file
{
    // Database settings
    "database": "postgres"
}
"""

result = load_json_preserving_comments(json_text)
print(result["value"])      # {'database': 'postgres'}
print(result["comments"])   # ['Configuration file', 'Database settings']
```

## Comment Types

### Line Comments

Use `//` for single-line comments:

```json
{
    // This is a line comment
    "key": "value"
}
```

### Block Comments

Use `/* */` for multi-line comments:

```json
{
    /*
     * This is a block comment
     * spanning multiple lines
     */
    "key": "value"
}
```

### Mixed Comments

You can mix both types:

```json
{
    // Line comment
    "setting1": "value1",
    /* Block comment */
    "setting2": "value2"
}
```

## Advanced Usage

### Using the Parser Class Directly

For more control, use the `JSONWithCommentsParser` class:

```python
from jsonclark import JSONWithCommentsParser

parser = JSONWithCommentsParser()

# Parse and get result
result = parser.parse('// Comment\n{"key": "value"}')

# Parse and preserve comments
result = parser.parse_with_comments('// Comment\n{"key": "value"}')
print(result["value"])      # {'key': 'value'}
print(result["comments"])   # ['Comment']
```

### Extracting Comments Only

If you only need to extract comments from JSON:

```python
from jsonclark import JSONWithCommentsParser

text = '// Comment 1\n/* Comment 2 */\n{}'
comments = JSONWithCommentsParser._extract_comments(text)
print(comments)  # ['Comment 1', 'Comment 2']
```

## Real-World Example

Here's a configuration file example:

```python
from jsonclark import load_json_with_comments

config_text = """
{
    // Server configuration
    "server": {
        "host": "0.0.0.0",
        // HTTP port
        "port": 8080,
        /* SSL settings */
        "ssl": {
            "enabled": true,
            "certificate": "/etc/ssl/cert.pem"
        }
    },
    
    // Database connection
    "database": {
        "type": "postgresql",
        "host": "localhost",
        /* Connection pool size */
        "poolSize": 20
    }
}
"""

config = load_json_with_comments(config_text)

print(f"Server: {config['server']['host']}:{config['server']['port']}")
print(f"Database: {config['database']['type']}")
print(f"Pool Size: {config['database']['poolSize']}")
```

## Data Structures

### JSONValue

Optional dataclass for representing JSON values with comment metadata:

```python
from jsonclark import JSONValue

value = JSONValue(
    value={"key": "value"},
    comments_before=["Opening comment"],
    comments_after=["Closing comment"]
)
```

## API Reference

### Functions

- `load_json_with_comments(text: str) -> Any`
  - Parse JSON with comments and return the parsed Python object
  - Raises `lark.exceptions.LarkError` for invalid JSON

- `load_json_preserving_comments(text: str) -> dict[str, Any]`
  - Parse JSON and return both value and comments
  - Returns `{"value": parsed_object, "comments": [list_of_comments]}`

### Classes

- `JSONWithCommentsParser`
  - Main parser class
  - Methods:
    - `parse(text: str) -> Any` - Parse JSON and return Python object
    - `parse_with_comments(text: str) -> dict[str, Any]` - Parse and preserve comments
    - `_extract_comments(text: str) -> list[str]` - Static method to extract comments

## Testing

### With Nox (Multi-version Testing)

Test across Python 3.9 - 3.13 using nox:

```bash
# Install nox with uv support
pip install nox-uv

# Run tests on all Python versions
nox

# Test specific version
nox -s tests-3.13

# Run only parser tests
nox -s tests_parser-3.13

# Run only CLI tests
nox -s tests_cli-3.13
```

### With Pytest

Run the comprehensive test suite:

```bash
pytest tests/ -v
```

All tests pass ✅

## Limitations

- Comments must follow C-style syntax (`//` and `/* */`)
- Comments inside strings are preserved as part of the string value
- The parser focuses on standard JSON data types (no trailing commas or unquoted keys)

## Requirements

- Python >= 3.10
- Lark >= 1.3.1

## License

MIT

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting a pull request.

```bash
pytest tests/test_parser.py
```
