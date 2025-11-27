"""Shared fixtures and utilities for tests."""

# Sample JSON data for testing
SIMPLE_OBJECT = '{"name": "test", "value": 123}'
SIMPLE_ARRAY = "[1, 2, 3]"

JSON_WITH_LINE_COMMENTS = """
{
    // User name
    "name": "Alice",
    // User age
    "age": 30
}
"""

JSON_WITH_BLOCK_COMMENTS = """
{
    /* User information */
    "name": "Bob",
    /* Age field */
    "age": 25
}
"""

COMPLEX_JSON = """
{
    // Server config
    "server": {
        "host": "localhost",
        // HTTP port
        "port": 8080,
        /* Enable SSL */
        "ssl": true
    },
    // Database settings
    "database": {
        "type": "postgresql",
        "host": "db.local",
        // Connection pool size
        "pool_size": 20
    }
}
"""


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "cli: mark test as CLI test")
    config.addinivalue_line("markers", "parser: mark test as parser test")
    config.addinivalue_line("markers", "interface: mark test as interface test")
