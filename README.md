[![PyPI - Version](https://img.shields.io/pypi/v/dmp-af)](https://pypi.org/project/dmp-af/)
[![GitHub Build](https://github.com/dmp-labs/dmp-af/workflows/PR%20checks/badge.svg)](https://github.com/dmp-labs/dmp-af/actions)

[![License](https://img.shields.io/:license-Apache%202-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0.txt)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dmp-af.svg)](https://pypi.org/project/dmp-af/)
[![PyPI - Downloads](https://img.shields.io/pepy/dt/dmp-af)](https://pypi.org/project/dmp-af/)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

# dmp-af: distributed dbt runs on Airflow

## Overview

**dmp-af** runs your dbt models in parallel on Airflow. Each model becomes an independent task while preserving
dependencies across domains.

**Built for scale.** Designed for large dbt projects (1000+ models)
and [data mesh architecture](https://www.datamesh-architecture.com/#what-is-data-mesh). Works with any project size.

![dmp-af](https://raw.githubusercontent.com/dmp-labs/dmp-af/main/docs/static/airflow_dag_layout.png)
![dbt-af3](https://raw.githubusercontent.com/dmp-labs/dmp-af/main/docs/static/airflow3_dag_layout.png)

### Why dmp-af?

1. **Domain-driven architecture** - Separate models by domain into different DAGs, run in parallel, perfect for data
   mesh
2. **dbt-first design** - All configuration in dbt model configs, analytics teams stay in dbt, no Airflow knowledge
   required
3. **Flexible scheduling** - Multiple schedules per model (`@hourly`, `@daily`, `@weekly`,
   `@monthly`, [and more](examples/manual_scheduling.md))
4. **Enterprise features** - Multiple dbt targets, configurable test strategies, built-in maintenance, Kubernetes
   support

## Installation

To install `dmp-af` run `pip install dmp-af`.

To contribute we recommend to use `uv` to install package dependencies.
Run `uv sync --all-packages --all-groups --all-extras` to install all dependencies.

## _dmp-af_ by Example

All tutorials and examples are located in the [examples](examples/README.md) folder.

To get basic Airflow DAGs for your dbt project, you need to put the following code into your `dags` folder:

```python
# LABELS: dag, airflow (it's required for airflow dag-processor)
from dmp_af.dags import compile_dmp_af_dags
from dmp_af.conf import Config, DbtDefaultTargetsConfig, DbtProjectConfig

# specify here all settings for your dbt project
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
    dry_run=False,  # set to True if you want to turn on dry-run mode
)

dags = compile_dmp_af_dags(
    manifest_path='/path/to/my_dbt_project/target/manifest.json',
    config=config,
)
for dag_name, dag in dags.items():
    globals()[dag_name] = dag
```

In _dbt_project.yml_ you need to set up default targets for all nodes in your project
(see [example](examples/dags/dbt_project.yml)):

```yaml
sql_cluster: "dev"
daily_sql_cluster: "dev"
py_cluster: "dev"
bf_cluster: "dev"
```

This will create Airflow DAGs for your dbt project.

Check out the documentation for more details [here](docs/docs.md).

## Key Features

**Auto-generated DAGs**

- Automatically creates Airflow DAGs from your dbt project
- Organizes by domain and schedule
- Handles dependencies across domains

**Idempotent runs**

- Each model is a separate Airflow task
- Date intervals passed to every run
- Reliable backfills and reruns

**Team-friendly**

- Analytics teams stay in dbt
- No Airflow DAG writing required
- Infrastructure handled automatically

## Requirements

`dmp-af` is tested with:

| Airflow version | Python versions | `dbt-core` versions |
|-----------------|-----------------|---------------------|
| 2.6.3           | ≥3.10,<3.12     | ≥1.7,<=1.10         |
| 2.7.3           | ≥3.10,<3.12     | ≥1.7,<=1.10         |
| 2.8.4           | ≥3.10,<3.12     | ≥1.7,<=1.10         |
| 2.9.3           | ≥3.10,<3.13     | ≥1.7,<=1.10         |
| 2.10.5          | ≥3.10,<3.13     | ≥1.7,<=1.10         |
| 2.11.0          | ≥3.10,<3.13     | ≥1.7,<=1.10         |
| 3.0.6           | ≥3.10,<3.13     | ≥1.7,≤1.10          |
| 3.1.3           | ≥3.10,<3.14     | ≥1.7,≤1.10          |

## Project Information

- [Docs](https://docs.dmp.af)
- [PyPI](https://pypi.org/project/dmp-af/)
- [Contributing](CONTRIBUTING.md)
- [Original dbt-af Project](https://github.com/Toloka/dbt-af)

## About this fork

This project is a fork of [Toloka AI BV's original repository](https://github.com/Toloka/dbt-af).
It includes substantial modifications by IJKOS & PARTNERS LTD.
This fork is not affiliated with or endorsed by Toloka AI BV.

The original project is licensed under the [Apache License 2.0](./LICENSE).

### Migrating from dbt-af

If you're currently using dbt-af and want to migrate to dmp-af, see our [Migration Guide](MIGRATION.md) for step-by-step
instructions.
