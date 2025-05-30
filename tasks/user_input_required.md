# User Input Required

This file lists actions that need to be performed manually by the user.

## Task EP11.2: Implement Pre-commit Hooks

The `.pre-commit-config.yaml` file has been created. The following steps need to be performed in your local development environment:

1.  **Install pre-commit:**
    ```bash
    pip install pre-commit
    # or, if you manage dev tools with a different method like pipx
    # pipx install pre-commit
    ```
2.  **Install the git hook scripts:**
    ```bash
    pre-commit install
    ```
3.  **Run pre-commit on all files to format and lint the current codebase:**
    ```bash
    pre-commit run --all-files
    ```
    This command will run `black`, `ruff`, and `mypy` as configured.
    -   `black` and `ruff --fix` will automatically reformat files if issues are found. Review these changes.
    -   `mypy` will report type errors. These might require manual code changes to resolve.
    -   If `mypy` reports too many errors initially that are hard to fix immediately, you can temporarily exclude problematic files or directories in `.pre-commit-config.yaml` under the `mypy` hook's `exclude` field, and address them incrementally. For example:
        ```yaml
        # .pre-commit-config.yaml
        # ...
        -   repo: https://github.com/pre-commit/mirrors-mypy
            rev: v1.7.1
            hooks:
            -   id: mypy
                additional_dependencies: ["pydantic>=2.0", "types-python-jose", "types-passlib"]
                exclude: ^(path/to/problematic_module/|another_file.py)
        ```
4.  **Commit any changes made by the hooks.**

    Addressing any issues reported by these tools (especially `mypy`) might require further code adjustments.
