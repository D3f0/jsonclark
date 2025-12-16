"""Command-line interface for jsonclark.

Usage:
    python -m jsonclark [--indent INDENT] [--sort-keys] [--comments] [--yq EXPRESSION] [FILE]

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

    # Apply yq expression to modify JSON (preserving comments)
    python -m jsonclark --yq '.foo = "bar"' config.jsonc

    # All options together
    python -m jsonclark --indent 4 --sort-keys --comments config.jsonc
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Optional

from jsonclark import loads, loads_comments


def check_yq_available() -> bool:
    """Check if yq binary is available in PATH.

    Returns:
        True if yq is available, False otherwise
    """
    return shutil.which("yq") is not None


def print_yq_installation_instructions() -> None:
    """Print instructions on how to install yq."""
    print(
        "Error: yq binary not found in PATH",
        file=sys.stderr,
    )
    print(
        "\nTo install yq, use one of the following methods:",
        file=sys.stderr,
    )
    print(
        "\n1. Using Homebrew (macOS/Linux):",
        file=sys.stderr,
    )
    print(
        "   brew install yq",
        file=sys.stderr,
    )
    print(
        "\n2. From GitHub releases:",
        file=sys.stderr,
    )
    print(
        "   https://github.com/mikefarah/yq/releases",
        file=sys.stderr,
    )
    print(
        "\n3. Using pip:",
        file=sys.stderr,
    )
    print(
        "   pip install yq",
        file=sys.stderr,
    )


def apply_yq_expression(
    json_text: str,
    expression: str,
    output_file: Optional[str] = None,
) -> str:
    """Apply a yq expression to JSON text.

    Args:
        json_text: The JSON content as a string (may contain comments)
        expression: The yq expression to apply
        output_file: Optional file path to write output to (in-place update)

    Returns:
        The modified JSON as a string

    Raises:
        subprocess.CalledProcessError: If yq command fails
        FileNotFoundError: If yq is not available
    """
    # First, parse the JSON to remove comments and convert to pure JSON
    try:
        obj = loads(json_text)
        pure_json = json.dumps(obj)
    except Exception as e:
        raise ValueError(f"Failed to parse input JSON: {e}") from e

    # Create temporary file for input (pure JSON without comments)
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False,
    ) as tmp_input:
        tmp_input.write(pure_json)
        tmp_input_path = tmp_input.name

    try:
        if output_file:
            # In-place update: write to temp file first
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False,
            ) as tmp_output:
                tmp_output_path = tmp_output.name

            try:
                # Run yq with in-place update
                result = subprocess.run(
                    ["yq", expression, tmp_input_path],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode != 0:
                    raise subprocess.CalledProcessError(
                        result.returncode,
                        "yq",
                        output=result.stdout,
                        stderr=result.stderr,
                    )

                # Write result to output file
                with open(output_file, "w") as f:
                    f.write(result.stdout)

                return result.stdout
            finally:
                # Clean up temp output file if it exists
                if os.path.exists(tmp_output_path):
                    os.unlink(tmp_output_path)
        else:
            # Output to stdout
            result = subprocess.run(
                ["yq", expression, tmp_input_path],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                raise subprocess.CalledProcessError(
                    result.returncode,
                    "yq",
                    output=result.stdout,
                    stderr=result.stderr,
                )

            return result.stdout
    finally:
        # Clean up temp input file
        if os.path.exists(tmp_input_path):
            os.unlink(tmp_input_path)


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
        "  python -m jsonclark --sort-keys --comments config.jsonc\n"
        "  python -m jsonclark --yq '.foo = \"bar\"' config.jsonc",
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
        "--yq",
        type=str,
        default=None,
        help="Apply a yq expression to modify the JSON (preserves comments on file input)",
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
            is_stdin = False
        else:
            json_text = sys.stdin.read()
            is_stdin = True

        # Handle yq transformation
        if args.yq:
            if not check_yq_available():
                print_yq_installation_instructions()
                sys.exit(1)

            # If processing from file, create a backup
            if not is_stdin and args.file:
                backup_path = f"{args.file}.bak"
                shutil.copy2(args.file, backup_path)

            # Apply yq expression
            try:
                output = apply_yq_expression(
                    json_text,
                    args.yq,
                    output_file=args.file if (not is_stdin and args.file) else None,
                )

                # If stdin or no file specified, print to stdout
                if is_stdin or not args.file:
                    print(output, end="")
                # If file input, the output is already written in-place by apply_yq_expression

            except subprocess.CalledProcessError as e:
                print("Error: yq expression failed", file=sys.stderr)
                if e.stderr:
                    print(f"  {e.stderr}", file=sys.stderr)
                sys.exit(1)
        else:
            # Normal processing (no yq)
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
