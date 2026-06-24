# Installation

This page covers how to install dmp-af and its dependencies.

## Requirements

Before installing dmp-af, ensure you have:

- Python 3.10, 3.11, 3.12, or 3.13
- Apache Airflow 2.6 or higher
- dbt-core 1.7 to 1.10

See [Prerequisites](prerequisites.md) for the full compatibility matrix.

## Installation Methods

### Standard Installation

Install dmp-af via pip:

```bash
pip install dmp-af
```

This installs the core package with all required dependencies.

### Optional Features

dmp-af supports several optional integrations:

#### Monte Carlo Data Integration

For Monte Carlo Data catalog integration:

```bash
pip install dmp-af[mcd]
```

This adds:

- `airflow-mcd>=0.3.3,<0.4.0`
- `pycarlo>=0.9`

#### Tableau Integration

For Tableau refresh tasks:

```bash
pip install dmp-af[tableau]
```

This adds:

- `tableauserverclient>=0.25.0,<0.26.0`

#### All Optional Features

To install everything:

```bash
pip install dmp-af[all]
```

### Development Installation

For contributors and developers:

```bash
# Clone the repository
git clone https://github.com/dmp-labs/dmp-af.git
cd dmp-af

# Using uv (recommended)
uv sync --all-packages --all-groups --all-extras

# Or using pip
pip install -e ".[dev]"
```

The development installation includes:

- Testing tools (pytest, pytest-cov)
- Linting tools (ruff, pre-commit)
- Example dependencies (dbt-postgres)
- Documentation tools

## Verifying Installation

After installation, verify that dmp-af is available:

```bash
python -c "import dmp_af; print(dmp_af.__version__)"
```

Check available CLI tools:

```bash
dmp-af-manifest-tests --help
```

## Airflow Integration

dmp-af works as an Airflow DAG generator. Make sure:

1. Airflow is installed and configured
2. Your `AIRFLOW_HOME` is set
3. The `dags/` folder is accessible

## dbt Integration

You'll need a dbt project with:

1. A valid `dbt_project.yml`
2. A configured `profiles.yml`
3. Compiled `manifest.json` (via `dbt compile`)

## Dependency Pinning

Some dependencies have version constraints for compatibility:

```python
# From pyproject.toml
dependencies = [
    "apache-airflow >=2.6,<3.3.0",
    "dbt-core >=1.7,<2",
    "pydantic >=1.10,<3.0.0",
    # ... other dependencies
]
```

If you encounter version conflicts, check the [compatibility matrix](prerequisites.md).

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'dmp_af'`:

1. Verify installation: `pip list | grep dmp-af`
2. Check Python environment: `which python`
3. Reinstall: `pip install --force-reinstall dmp-af`

### Airflow Version Conflicts

If Airflow dependencies conflict:

1. Create a fresh virtual environment
2. Install Airflow first: `pip install apache-airflow==2.10.5`
3. Then install dmp-af: `pip install dmp-af`

### dbt Version Issues

For dbt-core compatibility:

- Use dbt-core 1.7 to 1.10
- Specific adapters may have their own requirements
- Example for Postgres: `pip install dbt-postgres>=1.7.0,<2`

## Next Steps

Once installed, proceed to:

- [Quick Start](quick-start.md) - Create your first DAG
- [Docker Setup](docker-compose.md) - Run in containers
- [Prerequisites](prerequisites.md) - Detailed version info
