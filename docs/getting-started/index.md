# Getting Started with dmp-af

This guide will help you set up dmp-af and create your first distributed dbt runs on Airflow.

!!! info "Migrating from dbt-af?"
    If you're currently using the original dbt-af project and want to migrate to dmp-af, check out our **[Migration Guide](migration.md)** for step-by-step instructions.

## What You'll Learn

- Installing dmp-af and its prerequisites
- Setting up your environment
- Creating your first dmp-af DAG
- Running and monitoring your dbt models

## Prerequisites

Before you begin, make sure you have:

1. **Apache Airflow** (version 2.6 or higher)
2. **dbt-core** (version 1.7 to 1.10)
3. **Python** (3.10, 3.11, or 3.12)
4. A **dbt project** with a compiled manifest

See [Prerequisites](prerequisites.md) for detailed version compatibility information.

## Installation Options

You can install dmp-af in several ways:


### Add to your Airflow requirements.txt

```diff
+ dmp-af
```

### Via pip

```bash
pip install dmp-af
```

### With optional features

```bash
# Install with Monte Carlo Data integration
pip install dmp-af[mcd]

# Install with Tableau integration
pip install dmp-af[tableau]

# Install all optional features
pip install dmp-af[all]
```

### For development

```bash
# Clone the repository
git clone https://github.com/dmp-labs/dmp-af.git
cd dmp-af

# Install with uv (recommended)
uv sync --all-packages --all-groups --all-extras

# Or with pip
pip install -e ".[dev]"
```

## Quick Setup Guide

### Step 1: Compile Your dbt Manifest

Before using dmp-af, you need to compile your dbt project:

```bash
cd /path/to/your/dbt/project
dbt compile
```

This creates `target/manifest.json` which dmp-af uses to generate DAGs.

### Step 2: Configure dbt Project

Add cluster configurations to your `dbt_project.yml`:

```yaml
# dbt_project.yml

models:
  my_project:
    my_domain:
      sql_cluster: "dev"
      daily_sql_cluster: "dev"
      py_cluster: "dev"
      bf_cluster: "dev"
```

### Step 3: Create Your First DAG

Create a Python file in your Airflow `dags/` folder:

```python
# dags/my_dmp_af_dags.py
# LABELS: dag, airflow

from dmp_af.dags import compile_dmp_af_dags
from dmp_af.conf import Config, DbtDefaultTargetsConfig, DbtProjectConfig

config = Config(
    dbt_project=DbtProjectConfig(
        dbt_project_name='my_dbt_project',
        dbt_project_path='/path/to/my_dbt_project',
        dbt_models_path='/path/to/my_dbt_project/models',
        dbt_profiles_path='/path/to/my_dbt_project',
        dbt_target_path='/path/to/my_dbt_project/target',
        dbt_log_path='/path/to/my_dbt_project/logs',
        dbt_schema='my_dbt_schema',
    ),
    dbt_default_targets=DbtDefaultTargetsConfig(default_target='dev'),
    dry_run=False,
)

# Compile DAGs from manifest
dags = compile_dmp_af_dags(
    manifest_path='/path/to/my_dbt_project/target/manifest.json',
    config=config,
)

# Register DAGs with Airflow
for dag_name, dag in dags.items():
    globals()[dag_name] = dag
```

!!! note "Path to dbt project"
    Change `/path/to/my_dbt_project` to the path to your dbt project on your Airflow cluster.

### Step 4: Set Up Airflow Pools

dmp-af requires Airflow pools to manage concurrent task execution. 
You are going to see warnings if you don't set up pools. 

Create pools for each group of tasks:

```bash
# Via Airflow CLI
airflow pools set dbt_dev 4 "Development pool"
airflow pools set dbt_sensor_pool 10 "Sensor pool"
```

Or create them through the Airflow UI: **Admin** → **Pools** → **Add a new record**.

### Step 5: Verify in Airflow

1. Restart Airflow (if needed)
2. Navigate to the Airflow UI
3. Look for auto-generated DAGs named like `<domain>_<schedule>`
4. Enable and trigger a DAG to test

## What's Next?

Now that you have dmp-af set up, explore these topics:

- **[Quick Start](quick-start.md)** - Walk through a complete example
- **[Docker Setup](docker-compose.md)** - Run with Docker Compose
- **[Migration Guide](migration.md)** - Migrate from dbt-af to dmp-af
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides
- **[Configuration](../configuration/index.md)** - Fine-tune your setup

## Need Help?

- Check the [Tutorials](../tutorials/index.md) for detailed examples
- Review [Prerequisites](prerequisites.md) for compatibility issues
- Visit our [GitHub Issues](https://github.com/dmp-labs/dmp-af/issues) for support
