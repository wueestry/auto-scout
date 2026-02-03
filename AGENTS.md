# AGENTS.md

## Agentic Coding Handbook for `auto-scout`

Welcome, agentic coder! This document provides comprehensive guidance for automated and human agents contributing to the `auto-scout` repository. Follow these guidelines to ensure code consistency, robust automation, and seamless collaboration.

---

## 1. Build, Lint, and Test Commands

**Project Environment:**
- Python >= 3.12
- Dependencies managed via `pyproject.toml`

### 1.1. Installing Dependencies

- To install core and development dependencies (recommended, for agentic work):

```sh
pip install -e .
pip install -e .[dev]
```

### 1.2. Linting and Formatting

The project uses [ruff](https://docs.astral.sh/ruff/) for linting, formatting, and import sorting. Run:

```sh
ruff check .           # Lint the codebase
ruff format .          # Format the codebase
```

**Note:** Ruff covers style, lint, and sorting, providing fast feedback. Fix all warnings and errors.

### 1.3. Type Checking

Type checks are enforced using [mypy](http://mypy-lang.org/). Run:

```sh
mypy .
```

Fix all type errors before submitting or auto-generating code.

### 1.4. Testing

Currently, **no test files or runners** are present. If you add tests, use [pytest](https://docs.pytest.org/). Conventions for adding and running tests:

- Add tests in a `tests/` directory, named as `test_*.py`.
- Run all tests:
  ```sh
  pytest
  ```
- Run a single test file:
  ```sh
  pytest tests/test_filename.py
  ```
- Run a specific test case:
  ```sh
  pytest tests/test_filename.py::TestClassName::test_method_name
  ```

> **Agentic action:** If you add a test, also update AGENTS.md with examples, and ensure `pytest` is added to dev dependencies if not present.

---

## 2. Code Style Guidelines

### 2.1. Imports
- Use absolute imports within the project: `from auto_scout.module import Foo`.
- Standard library imports first, third-party second, project imports last (ruff will enforce).
- No wildcard imports (`from x import *`)—import only what is needed.

### 2.2. Formatting
- Use `ruff format .` for auto-formatting.
- Indent with 4 spaces.
- Maximum line length: 88 characters (ruff/mypy/black-style).
- Use single quotes or double quotes consistently (ruff will autocorrect).
- Leave one blank line between top-level function/class definitions.
- Remove unused imports and variables (ruff will flag and autocorrect).

### 2.3. Type Annotations
- **All** function arguments and return values must use type hints (`def foo(a: int) -> None:`).
- Use concrete types where possible (`list[str]`, `dict[str, int]`).
- Mark variables with types when unclear from context.
- Use `Optional` (or `| None`) for values that may be null.
- Prefer built-in generics (list[str]) over `List[str]` (no typing import unless needed).
- Use `Any` only as a last resort, and minimize its use.

### 2.4. Naming Conventions
- **Functions:** lower_snake_case
- **Variables:** lower_snake_case
- **Classes:** PascalCase
- **Constants:** UPPER_SNAKE_CASE
- **Modules/Files:** lower_snake_case.py
- Be descriptive but concise. Avoid ambiguity (e.g., prefer `host_ip` over `ip1`).
- Do not use misleading single-letter variable names.

### 2.5. Error Handling
- Use exceptions for error handling (not exit codes or silent failures).
- Catch only exceptions you expect and can handle. Avoid broad `except:` blocks.
- Use `logging` or `rich` for error output, not plain `print` for errors. (For normal user messages, `print` or `rich` is acceptable.)
- Surface clear, actionable error messages.

### 2.6. Docstrings & Comments
- All Public functions/classes/modules **must** have a concise, informative docstring.
- Use triple quotes (`"""`) for docstrings.
- Block comments where clarification is needed; avoid obvious commentary.
- Explain *why*, not just *what*.

### 2.7. File/Module Structure
- Group functions and classes by purpose; avoid overly long files (>300 lines).
- Each submodule (e.g., utils, scans) should be logically cohesive.
- Place new utilities in `auto_scout/utils/` unless domain-specific (elsewhere).

### 2.8. Dependency Management
- Add runtime dependencies to `[project.dependencies]` in `pyproject.toml`.
- Add dev tools (test, lint, type) to `[dependency-groups.dev]`.
- Never install dependencies outside of `pyproject.toml` without prior agreement.

### 2.9. Automation and Agents
- Document new agentic commands, conventions, or automations here.
- Follow all style, lint, and type-checking rules even for generated code.
- Add instructions for running/triggering agents if created.

---

## 3. Cursor and Copilot Rules

_No Cursor or Copilot rules detected._ If these files are added, update this section.

---

## 4. Common Patterns and Anti-Patterns

- **Use:**
  - Type annotations on everything
  - Descriptive variable and function names
  - Exceptions + clear error messages
  - Automated linting/formatting (ruff)
  - Standard testing conventions if tests are added

- **Avoid:**
  - Unused imports/variables
  - Bare `except:`
  - Implicit types
  - Mixed tabs/spaces
  - Large classes (>300 lines)

---

## 5. Open Tasks for Agents

- [ ] Establish first test suite with pytest
- [ ] Document custom agentic workflows if/when added
- [ ] Propose Cursor, Copilot, or other automated rule files (and document here)

---

**Happy agentic hacking! Ensure all code you produce matches these standards!**
