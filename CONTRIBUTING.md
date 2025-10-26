# Contributing to dmp-af

Thank you for your interest in contributing to dmp-af!

## Quick Links

📖 **[Full Contributing Guide](docs/development/contributing.md)** - Detailed guide with PR workflow, code style, commit messages, and testing

📋 **[Release Process](docs/development/releases.md)** - How semantic versioning and releases work

🧪 **[Testing Guide](docs/development/testing.md)** - Running tests with Dagger

## About This Project

This project is a fork of [dbt-af](https://github.com/Toloka/dbt-af) by Toloka AI BV, maintained by IJKOS & PARTNERS LTD. We welcome contributions from the community.

## Quick Start

### Reporting Issues

If you find a bug or have a feature request:
1. Check if the issue already exists in the [Issues](https://github.com/dmp-labs/dmp-af/issues) section
2. If not, create a new issue with a clear description
3. Include relevant details such as:
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (Python version, Airflow version, etc.)

### Submitting Pull Requests

1. Fork the repository and create a feature branch
2. Make your changes following our [code style guidelines](docs/development/contributing.md#code-style)
3. Write tests and ensure they pass
4. Use [conventional commit messages](docs/development/contributing.md#commit-messages) (e.g., `feat:`, `fix:`)
5. Update documentation as needed
6. Submit a PR and fill out the template

See the [full PR workflow guide](docs/development/contributing.md#submitting-pull-requests) for details.

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/dmp-af.git
cd dmp-af

# Install dependencies using uv (recommended)
uv sync --all-packages --all-groups --all-extras

# Install pre-commit hooks (validates commit messages)
uv run pre-commit install --hook-type commit-msg
```

### Running Tests

```bash
# Test with specific versions using Dagger
dagger call -m ./.ci tests test-one-versions-combination \
  --python-version=3.12 \
  --airflow-version=2.11.0 \
  --dbt-version=1.10 \
  --with-running-airflow-tasks
```

See the [full testing guide](docs/development/testing.md) for more options.

## Key Guidelines

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

## Questions?

If you have questions about contributing, feel free to:
- Open an issue for discussion
- Check the [full contributing guide](docs/development/contributing.md)
- Contact the maintainers

## License

By contributing to this project, you agree that your contributions will be licensed under the Apache License 2.0, the same license as the project.
