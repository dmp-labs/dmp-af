# Contributing to dmp-af

Thank you for your interest in contributing to dmp-af!

## About This Project

This project is a fork of [dbt-af](https://github.com/Toloka/dbt-af) by Toloka AI BV, maintained by IJKOS & PARTNERS LTD. We welcome contributions from the community.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:
1. Check if the issue already exists in the [Issues](https://github.com/ijkos/dmp-af/issues) section
2. If not, create a new issue with a clear description
3. Include relevant details such as:
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (Python version, Airflow version, etc.)

### Submitting Pull Requests

1. Fork the repository
2. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Write or update tests as needed
5. Ensure all tests pass
6. Commit your changes with clear, descriptive commit messages
7. Push to your fork and submit a pull request

### Development Setup

To set up your development environment:

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/dmp-af.git
cd dmp-af

# Install dependencies using uv (recommended)
uv sync --all-packages --all-groups --all-extras

# Or using pip
pip install -e ".[dev]"
```

### Code Style

- Follow the existing code style in the project
- Use `ruff` for linting (configured in `pyproject.toml`)
- Write clear, descriptive variable and function names
- Add docstrings to public functions and classes

### Testing

This project uses [Dagger](https://dagger.io/) for running tests in isolated containers to ensure consistency across different environments.

#### Running Tests Locally

**Prerequisites:**
- Install [Dagger CLI](https://docs.dagger.io/install)

**Run tests for a specific configuration:**

```bash
# Test with specific Python, Airflow, and dbt versions
dagger call -m ./.ci tests test-one-versions-combination \
  --python-version=3.12 \
  --airflow-version=2.11.0 \
  --dbt-version=1.10 \
  --with-running-airflow-tasks
```

**Run tests for all supported configurations:**

```bash
# Get the test matrix
dagger call -m ./.ci tests get-versions-matrix export --path=./matrix.json

# Run tests for each configuration in the matrix
# (See .github/workflows/integration_tests.yml for the full automation)
```

#### Quick Local Testing (without Dagger)

For quick iteration during development, you can also run tests directly with pytest:

```bash
pytest
```

Note: The CI pipeline uses Dagger to test against multiple Python, Airflow, and dbt versions. Make sure your changes pass the full test suite before submitting a pull request.

## Questions?

If you have questions about contributing, feel free to:
- Open an issue for discussion
- Contact the maintainers

## License

By contributing to this project, you agree that your contributions will be licensed under the Apache License 2.0, the same license as the project.
