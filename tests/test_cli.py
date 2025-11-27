"""Tests for the command-line interface."""

import subprocess
import sys
import tempfile
import os
import json
import pytest


def run_cli(*args):
    """Run the CLI and return (stdout, stderr, returncode)."""
    cmd = [sys.executable, "-m", "jsonclark"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode


# Basic CLI tests
@pytest.mark.cli
def test_cli_help():
    """Test --help option."""
    stdout, stderr, code = run_cli("--help")
    assert code == 0
    assert "Pretty-print JSON" in stdout


@pytest.mark.cli
def test_cli_version():
    """Test --version option."""
    stdout, stderr, code = run_cli("--version")
    assert code == 0
    assert "0.1.0" in stdout


@pytest.mark.cli
def test_cli_stdin_basic():
    """Test parsing from stdin."""
    json_text = '{"name": "test", "value": 123}'
    result = subprocess.run(
        [sys.executable, "-m", "jsonclark"],
        input=json_text,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["name"] == "test"


@pytest.mark.cli
def test_cli_stdin_with_comments():
    """Test parsing from stdin with comments."""
    json_text = '{"key": "value"}  // comment'
    result = subprocess.run(
        [sys.executable, "-m", "jsonclark"],
        input=json_text,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["key"] == "value"


# File input tests
@pytest.mark.cli
def test_cli_file_input():
    """Test parsing from file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonc", delete=False) as f:
        f.write('{"x": 1, "y": 2}  // comment')
        f.flush()

        try:
            stdout, stderr, code = run_cli(f.name)
            assert code == 0
            output = json.loads(stdout)
            assert output["x"] == 1
        finally:
            os.unlink(f.name)


# Formatting tests
@pytest.mark.cli
def test_cli_indent_2():
    """Test default indentation (2 spaces)."""
    json_text = '{"a": {"b": 1}}'
    result = subprocess.run(
        [sys.executable, "-m", "jsonclark", "--indent", "2"],
        input=json_text,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "  " in result.stdout


@pytest.mark.cli
def test_cli_indent_4():
    """Test 4-space indentation."""
    json_text = '{"a": {"b": 1}}'
    result = subprocess.run(
        [sys.executable, "-m", "jsonclark", "--indent", "4"],
        input=json_text,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "    " in result.stdout


@pytest.mark.cli
def test_cli_sort_keys():
    """Test --sort-keys option."""
    json_text = '{"z": 1, "a": 2, "m": 3}'
    result = subprocess.run(
        [sys.executable, "-m", "jsonclark", "--sort-keys"],
        input=json_text,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = result.stdout
    a_pos = output.find('"a"')
    m_pos = output.find('"m"')
    z_pos = output.find('"z"')
    assert a_pos < m_pos < z_pos


# Comment extraction tests
@pytest.mark.cli
def test_cli_show_comments():
    """Test --comments option."""
    json_text = '// Comment 1\n// Comment 2\n{"key": "value"}'
    result = subprocess.run(
        [sys.executable, "-m", "jsonclark", "--comments"],
        input=json_text,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "// Comment 1" in result.stdout


@pytest.mark.cli
def test_cli_no_comments_without_flag():
    """Test that comments are stripped without --comments."""
    json_text = '// Comment\n{"key": "value"}'
    result = subprocess.run(
        [sys.executable, "-m", "jsonclark"],
        input=json_text,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "// Comment" not in result.stdout


@pytest.mark.cli
def test_cli_show_block_comments():
    """Test showing block comments."""
    json_text = '/* Block comment */\n{"x": 1}'
    result = subprocess.run(
        [sys.executable, "-m", "jsonclark", "--comments"],
        input=json_text,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "// Block comment" in result.stdout


# Combined options tests
@pytest.mark.cli
def test_cli_all_options():
    """Test using all options together."""
    json_text = '{"z_name": "test", "a_value": 123}'
    result = subprocess.run(
        [sys.executable, "-m", "jsonclark", "--indent", "4", "--sort-keys"],
        input=json_text,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "    " in result.stdout
    output = result.stdout
    a_pos = output.find('"a_value"')
    z_pos = output.find('"z_name"')
    assert a_pos < z_pos


@pytest.mark.cli
def test_cli_file_with_options():
    """Test file input with multiple options."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonc", delete=False) as f:
        f.write('{\n    // Comments\n    "z": 1,\n    "a": 2\n}')
        f.flush()

        try:
            stdout, stderr, code = run_cli("--sort-keys", "--indent", "4", f.name)
            assert code == 0
            assert "    " in stdout
        finally:
            os.unlink(f.name)


# Error handling tests
@pytest.mark.cli
def test_cli_invalid_json():
    """Test error on invalid JSON."""
    json_text = '{"incomplete":'
    result = subprocess.run(
        [sys.executable, "-m", "jsonclark"],
        input=json_text,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Error" in result.stderr


@pytest.mark.cli
def test_cli_file_not_found():
    """Test error on missing file."""
    stdout, stderr, code = run_cli("/nonexistent/file.json")
    assert code == 1
    assert "File not found" in stderr


# Complex structure tests
@pytest.mark.cli
def test_cli_nested_structure():
    """Test with deeply nested structure."""
    json_text = '{"server": {"http": {"host": "localhost", "port": 8080}}}'
    result = subprocess.run(
        [sys.executable, "-m", "jsonclark"],
        input=json_text,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["server"]["http"]["port"] == 8080


@pytest.mark.cli
def test_cli_array_structure():
    """Test with arrays."""
    json_text = '[{"id": 1}, {"id": 2}]'
    result = subprocess.run(
        [sys.executable, "-m", "jsonclark"],
        input=json_text,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert len(output) == 2


# Integration tests
@pytest.mark.cli
def test_cli_realistic_config():
    """Test with realistic configuration file."""
    config = '{"app": {"name": "MyApp", "version": "1.0.0"}, "server": {"port": 8080}}'
    result = subprocess.run(
        [sys.executable, "-m", "jsonclark", "--sort-keys"],
        input=config,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["app"]["name"] == "MyApp"


@pytest.mark.cli
def test_cli_pipe_compatibility():
    """Test using CLI in a pipe."""
    json_text = '{"b": 2, "a": 1}'
    result = subprocess.run(
        [sys.executable, "-m", "jsonclark", "--sort-keys"],
        input=json_text,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert parsed["a"] == 1
    assert parsed["b"] == 2
