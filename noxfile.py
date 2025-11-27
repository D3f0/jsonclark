from nox import Session, options
from nox_uv import session

options.default_venv_backend = "uv"

# Python versions to test
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]

# Dependencies
LINT_DEPS = ["ruff>=0.1.0", "black>=23.0.0"]
TYPE_CHECK_DEPS = ["mypy>=1.0.0"]


@session(python=PYTHON_VERSIONS)
def tests(session: Session) -> None:
    """Run pytest tests on specified Python versions."""
    session.install("-e", ".[dev]")
    session.run("pytest", "tests/", "-v", "--tb=short")


@session(python=PYTHON_VERSIONS)
def tests_cli(session: Session) -> None:
    """Run only CLI tests."""
    session.install("-e", ".[dev]")
    session.run("pytest", "tests/", "-v", "-m", "cli")


@session(python="3.13")
def lint(session: Session) -> None:
    """Run linting checks (on Python 3.13 only)."""
    session.install(*LINT_DEPS)
    session.run("ruff", "check", "src/", "tests/")


@session(python="3.13")
def type_check(session: Session) -> None:
    """Run type checking with mypy (on Python 3.13 only)."""
    session.install("-e", ".", *TYPE_CHECK_DEPS)
    session.run("mypy", "src/jsonclark/", "--ignore-missing-imports")


@session(python="3.13")
def coverage(session: Session) -> None:
    """Run tests with coverage reporting (on Python 3.13 only)."""
    session.install("-e", ".[dev]", "pytest-cov>=4.0.0")
    session.run(
        "pytest",
        "tests/",
        "--cov=src/jsonclark",
        "--cov-report=html",
        "--cov-report=term-missing",
    )
