# Testing

Learn how to run tests for dmp-af development.

## Test Framework

dmp-af uses [Dagger](https://dagger.io/) for running tests in isolated containers across multiple versions.

## Prerequisites

Install Dagger CLI:

```bash
# macOS
brew install dagger/tap/dagger

# Linux
curl -L https://dl.dagger.io/dagger/install.sh | sh

# Or see https://docs.dagger.io/install
```

## Running Tests

### Test One Version Combination

```bash
dagger call -m ./.ci tests test-one-versions-combination \
  --python-version=3.12 \
  --airflow-version=2.11.0 \
  --dbt-version=1.10 \
  --with-running-airflow-tasks
```

### Get Test Matrix

```bash
dagger call -m ./.ci tests get-versions-matrix export --path=./matrix.json
cat matrix.json
```

### Quick Local Testing

For rapid iteration without Dagger:

```bash
pytest
```

Note: This only tests your current environment. CI tests all version combinations.

## Test Structure

```
tests/
  ├── test_dags.py           # DAG compilation tests
  ├── test_operators.py      # Operator tests
  ├── test_config.py         # Configuration tests
  └── integration/           # Integration tests
```

## Contributing

See [Contributing Guide](contributing.md) for development setup and guidelines.
