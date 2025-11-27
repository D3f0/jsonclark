"""Command-line interface for jsonclark.

Usage:
    python -m jsonclark [--indent INDENT] [--sort-keys] [--comments] [FILE]

Examples:
    # Pretty-print JSON from stdin
    cat config.jsonc | python -m jsonclark

    # Pretty-print with custom indentation
    cat config.jsonc | python -m jsonclark --indent 2

    # Sort keys in output
    cat config.jsonc | python -m jsonclark --sort-keys

    # Show extracted comments
    cat config.jsonc | python -m jsonclark --comments

    # Pretty-print from file
    python -m jsonclark config.jsonc

    # All options together
    python -m jsonclark --indent 4 --sort-keys --comments config.jsonc
"""

import sys
import json
import argparse
from typing import Any, Optional

from jsonclark import loads, loads_comments


def format_json(
    obj: Any,
    indent: Optional[int] = None,
    sort_keys: bool = False,
    show_comments: bool = False,
    comments: Optional[list[str]] = None,
) -> str:
    """Format a JSON object as a string.

    Args:
        obj: The object to format
        indent: Number of spaces for indentation (None = compact)
        sort_keys: Whether to sort dictionary keys
        show_comments: Whether to show comments above the JSON
        comments: List of comments to display

    Returns:
        Formatted JSON string
    """
    output = ""

    # Add comments if requested
    if show_comments and comments:
        for comment in comments:
            output += f"// {comment}\n"
        if output:
            output += "\n"

    # Format the JSON
    json_str = json.dumps(
        obj,
        indent=indent,
        sort_keys=sort_keys,
        ensure_ascii=False,
    )
    output += json_str

    return output


def main() -> None:
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        prog="jsonclark",
        description="Pretty-print JSON with comment support",
        epilog="Examples:\n"
        "  cat config.jsonc | python -m jsonclark\n"
        "  python -m jsonclark --indent 2 config.jsonc\n"
        "  python -m jsonclark --sort-keys --comments config.jsonc",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Input file (default: stdin)",
    )

    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Number of spaces for indentation (default: 2)",
    )

    parser.add_argument(
        "--sort-keys",
        action="store_true",
        help="Sort dictionary keys in output",
    )

    parser.add_argument(
        "--comments",
        action="store_true",
        help="Show extracted comments in output",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    args = parser.parse_args()

    try:
        # Read input
        if args.file:
            with open(args.file, "r") as f:
                json_text = f.read()
        else:
            json_text = sys.stdin.read()

        # Parse JSON
        if args.comments:
            obj, comments = loads_comments(json_text)
        else:
            obj = loads(json_text)
            comments = None

        # Format output
        output = format_json(
            obj,
            indent=args.indent,
            sort_keys=args.sort_keys,
            show_comments=args.comments,
            comments=comments,
        )

        print(output)

    except FileNotFoundError as e:
        print(f"Error: File not found: {e.filename}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
