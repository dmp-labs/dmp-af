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

#### Before You Start

1. Fork the repository
2. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Making Changes

1. Make your changes following the code style guidelines
2. Write or update tests as needed (see [Testing](#testing) section)
3. Ensure all tests pass locally
4. Update documentation if needed (see [Documentation](#documentation) section)
5. Use conventional commit messages (see [Commit Messages](#commit-messages) section)

#### Submitting Your PR

1. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
2. Create a pull request on GitHub
3. Fill out the PR template with:
   - **Clear description**: Explain what your PR does and why
   - **Type of change**: Indicate if it's a bug fix, feature, breaking change, etc.
   - **Testing evidence**: Show that you've tested your changes
   - **Documentation updates**: Confirm docs are updated if needed
   - **Meaningful context**: Link to related issues, explain design decisions

#### PR Review Process

- Maintainers will review your PR and may request changes
- Address review comments by pushing new commits to your branch
- Once approved, a maintainer will merge your PR
- Your changes will be included in the next release

#### What Maintainers Look For

✅ **Good PRs include:**
- Clear, meaningful description of changes
- Tests that prove the fix/feature works
- Updated documentation (docstrings, guides, README if needed)
- Conventional commit messages for automatic versioning
- Context about why the change is needed

❌ **PRs may be rejected if they:**
- Lack tests for new functionality
- Break existing tests
- Don't follow code style guidelines
- Lack documentation updates
- Have unclear or missing descriptions
- Use non-conventional commit messages

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

### Commit Messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automatic semantic versioning. Your commit messages must follow this format:

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` - New feature (triggers minor version bump)
- `fix:` - Bug fix (triggers patch version bump)
- `docs:` - Documentation changes only
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

**Breaking changes:**
- Add `!` after type: `feat!:` or `fix!:`
- Or add `BREAKING CHANGE:` in footer (triggers major version bump)

**Examples:**
```bash
feat: add support for dbt snapshots in maintenance DAGs
fix: resolve dependency resolution for cross-domain sources
docs: update contributing guide with PR template info
feat!: change configuration structure for domain schedules
```

A pre-commit hook validates commit messages. Install it with:
```bash
uv run pre-commit install --hook-type commit-msg
```

See [releases.md](releases.md) for more details on versioning.

### Documentation

Update documentation when you:

- Add new features (update user guides, API docs)
- Change behavior (update relevant docs and CHANGELOG.md)
- Fix bugs that affect documented behavior
- Add new configuration options

**Documentation locations:**
- `docs/` - User-facing documentation (built with MkDocs)
- Docstrings - In-code documentation for functions and classes
- `CHANGELOG.md` - Automatically generated, but you can preview changes

**Preview documentation locally:**
```bash
make docs-serve   # Visit http://localhost:8000
```

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
