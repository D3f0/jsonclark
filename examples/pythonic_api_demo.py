"""Demonstration of Pythonic API - similar to json module."""

import jsonclark
import io

print("=" * 70)
print("jsonclark - Pythonic API Demo")
print("=" * 70)
print()

# Example 1: Basic loads() - like json.loads()
print("Example 1: loads() - Parse JSON string")
print("-" * 70)
json_with_comments = """
{
    // Application name
    "app": "MyApp",
    // Version number
    "version": "2.0.0"
}
"""

data = jsonclark.loads(json_with_comments)
print(f"Data: {data}")
print(f"App: {data['app']}")
print(f"Version: {data['version']}")
print()

# Example 2: load() from file - like json.load()
print("Example 2: load() - Parse from file object")
print("-" * 70)
config_text = """
{
    // Server configuration
    "server": {
        "host": "localhost",
        // HTTP port
        "port": 8080
    }
}
"""

fp = io.StringIO(config_text)
config = jsonclark.load(fp)
print(f"Config: {config}")
print(f"Server running on {config['server']['host']}:{config['server']['port']}")
print()

# Example 3: loads_comments() - Extract comments along with data
print("Example 3: loads_comments() - Parse with comment extraction")
print("-" * 70)
json_with_multiple_comments = """
// Configuration file
// Last updated: 2024-01-15
{
    // Database settings
    "database": "postgresql",
    /* Connection pool size */
    "pool": 20
}
"""

data, comments = jsonclark.loads_comments(json_with_multiple_comments)
print(f"Data: {data}")
print(f"Comments found ({len(comments)}):")
for i, comment in enumerate(comments, 1):
    print(f"  {i}. {comment}")
print()

# Example 4: load_comments() from file
print("Example 4: load_comments() - Parse file with comment extraction")
print("-" * 70)
fp = io.StringIO('// API config\n{"endpoint": "https://api.example.com"}')
api_config, api_comments = jsonclark.load_comments(fp)
print(f"Config: {api_config}")
print(f"Comments: {api_comments}")
print()

# Example 5: extract_comments() - Just get the comments
print("Example 5: extract_comments() - Extract comments only")
print("-" * 70)
json_text = """
// TODO: Add more settings
/* Configuration for testing environment */
{"env": "test"}
"""

comments = jsonclark.extract_comments(json_text)
print(f"Extracted comments: {comments}")
print()

# Example 6: Complex nested structure
print("Example 6: Complex nested structure with comments")
print("-" * 70)
complex_config = """
{
    // Server settings
    "server": {
        "http": {
            "host": "0.0.0.0",
            // HTTP port
            "port": 8080
        },
        // HTTPS configuration
        "https": {
            "port": 8443,
            /* Certificate path */
            "cert": "/etc/ssl/cert.pem"
        }
    },
    
    // Database configuration
    "database": {
        "type": "postgresql",
        "host": "db.example.com",
        // Connection timeout in seconds
        "timeout": 30
    }
}
"""

config = jsonclark.loads(complex_config)
print(f"HTTP Port: {config['server']['http']['port']}")
print(f"HTTPS Port: {config['server']['https']['port']}")
print(f"Database Type: {config['database']['type']}")
print(f"DB Timeout: {config['database']['timeout']}s")
print()

# Example 7: Comparison with json module API
print("Example 7: API comparison with json module")
print("-" * 70)
print("json module:")
print("  - json.loads(s) -> dict")
print("  - json.load(fp) -> dict")
print()
print("jsonclark module (Pythonic):")
print("  - jsonclark.loads(s) -> JSONDict (full dict compatibility)")
print("  - jsonclark.load(fp) -> JSONDict")
print("  - jsonclark.loads_comments(s) -> (JSONDict, [comments])")
print("  - jsonclark.load_comments(fp) -> (JSONDict, [comments])")
print("  - jsonclark.extract_comments(s) -> [comments]")
print()

# Example 8: Dict/List compatibility
print("Example 8: Full dict/list compatibility")
print("-" * 70)
data1 = jsonclark.loads('{"x": 1, "y": 2}')
data2 = {"x": 1, "y": 2}

print(f"JSONDict instance: {data1}")
print(f"Regular dict:      {data2}")
print(f"Are they equal? {data1 == data2}")
print("Can use in functions expecting dict? Yes!")


def process_config(config: dict):
    return f"Config keys: {', '.join(config.keys())}"


print(f"Result: {process_config(data1)}")
print()

print("=" * 70)
print("All examples completed!")
print("=" * 70)
