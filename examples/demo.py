"""Demonstration of JSON parser with comment support."""

from jsonclark import load_json_with_comments, load_json_preserving_comments

# Example 1: Parse JSON with line comments
print("Example 1: JSON with line comments")
print("=" * 50)
json_with_line_comments = """
{
    // Application configuration
    "app": "MyApp",
    // Version information
    "version": "1.0.0",
    // Features list
    "features": [
        "feature1",  // First feature
        "feature2"   // Second feature
    ]
}
"""
result = load_json_with_comments(json_with_line_comments)
print("Parsed result:")
print(result)
print()

# Example 2: Parse JSON with block comments
print("Example 2: JSON with block comments")
print("=" * 50)
json_with_block_comments = """
{
    /* Application name and version */
    "app": "MyApp",
    "version": "1.0.0",
    /* Configuration settings */
    "settings": {
        /* Debug mode */
        "debug": true,
        /* Log level */
        "logLevel": "INFO"
    }
}
"""
result = load_json_with_comments(json_with_block_comments)
print("Parsed result:")
print(result)
print()

# Example 3: Preserve comments
print("Example 3: Preserve comments while parsing")
print("=" * 50)
json_text = """
// Configuration file
{
    // User settings
    "user": "admin",
    /* Database connection info */
    "db": {
        "host": "localhost",
        "port": 5432
    }
}
"""
result = load_json_preserving_comments(json_text)
print("Parsed value:")
print(result["value"])
print("\nExtracted comments:")
for comment in result["comments"]:
    print(f"  - {comment}")
print()

# Example 4: Complex configuration with mixed comments
print("Example 4: Complex configuration with mixed comments")
print("=" * 50)
complex_config = """
{
    // Server configuration
    "server": {
        "host": "0.0.0.0",
        // Port number for HTTP server
        "port": 8080,
        /* SSL/TLS settings */
        "ssl": {
            "enabled": false,
            "certificate": "/path/to/cert.pem"
        }
    },
    // Database configuration
    "database": {
        "type": "postgresql",
        /* Connection pool size */
        "poolSize": 10
    }
}
"""
result = load_json_with_comments(complex_config)
print("Server configuration:")
print(f"  Host: {result['server']['host']}")
print(f"  Port: {result['server']['port']}")
print(f"  SSL Enabled: {result['server']['ssl']['enabled']}")
print("\nDatabase configuration:")
print(f"  Type: {result['database']['type']}")
print(f"  Pool Size: {result['database']['poolSize']}")
