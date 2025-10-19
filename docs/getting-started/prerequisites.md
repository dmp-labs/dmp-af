# Prerequisites

This page outlines the system requirements and compatibility information for dmp-af.

## Version Compatibility Matrix

dmp-af is tested and verified to work with the following version combinations:

| Airflow Version | Python Versions | dbt-core Versions |
|-----------------|-----------------|-------------------|
| 2.6.3           | ≥3.10, <3.12    | ≥1.7, ≤1.10       |
| 2.7.3           | ≥3.10, <3.12    | ≥1.7, ≤1.10       |
| 2.8.4           | ≥3.10, <3.12    | ≥1.7, ≤1.10       |
| 2.9.3           | ≥3.10, <3.13    | ≥1.7, ≤1.10       |
| 2.10.5          | ≥3.10, <3.13    | ≥1.7, ≤1.10       |
| 2.11.0          | ≥3.10, <3.13    | ≥1.7, ≤1.10       |

!!! tip "Latest Versions"
    We recommend using the latest compatible versions of Airflow and dbt-core for the best experience.

## System Requirements

### Python

- **Version**: 3.10, 3.11, or 3.12
- **Package Manager**: pip, poetry, or uv

### Apache Airflow

Check [Running Airflow in Docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)
and [Airflow Production Deployment](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/production-deployment.html)
official guides.

- **Version**: 2.6 or higher
- **Configuration**:
    - Working Airflow installation with scheduler and webserver
    - Access to Airflow's `dags/` folder
    - Configured database backend (Postgres recommended for production)

### dbt

- **Version**: dbt-core 1.7 to 1.10
- **Adapter**: Any dbt adapter (Postgres, Snowflake, BigQuery, etc.)
- **Files Needed**:
    - Compiled `manifest.json` from your dbt project
    - Valid `profiles.yml` configuration
    - Accessible dbt project directory in airflow

### Database

A dbt-compatible database for your data transformations:

- PostgreSQL
- Snowflake
- BigQuery
- Redshift
- Databricks
- Any other dbt-supported warehouse

Make sure that database is accessible from Airflow.

## Airflow Pools

dmp-af requires at least two Airflow pools to be configured:

1. **dbt execution pool** - Controls concurrent dbt tasks
    - Name: Based on your target (e.g., `dbt_dev`, `dbt_prod`)
    - Slots: Start with 4-8, adjust based on resources

2. **dbt sensor pool** - For dependency sensors
    - Name: `dbt_sensor_pool`
    - Slots: 10-20 recommended, adjust based on resources

Create via CLI:

```bash
airflow pools set dbt_dev 8 "Development environment"
airflow pools set dbt_sensor_pool 20 "Sensor pool for dependencies"
```

## Optional Dependencies

### For Monte Carlo Data Integration

Required versions:

- `airflow-mcd >=0.3.3, <0.4.0`
- `pycarlo >=0.9`

Install with:

```bash
pip install dmp-af[mcd]
```

### For Tableau Integration

Required versions:

- `tableauserverclient >=0.25.0, <0.26.0`

Install with:

```bash
pip install dmp-af[tableau]
```

### For Kubernetes Tasks

Required provider:

- `apache-airflow-providers-cncf-kubernetes >=7.0.0` (included automatically)

Additional requirements:

- Access to a Kubernetes cluster
- Configured `KubernetesExecutor` or `KubernetesPodOperator`
- Appropriate RBAC permissions

## Development Requirements

For contributing or running tests:

- `pytest >=7.4.0`
- `pytest-cov >=4.1.0`
- `ruff ==0.13.1`
- `pre-commit ==3.8.0`
- [Dagger](https://dagger.io/) (for integration tests)

## Environment Setup

### Minimum Setup

1. Python environment (virtualenv, conda, or uv)
2. Running Apache Airflow
3. dbt project with compiled manifest
4. Database connection configured

### Recommended Setup

1. Isolated virtual environment
2. Running Apache Airflow
3. dbt project with version control
4. Separate development and production targets
5. Monitoring and logging configured


## Network Requirements

Ensure connectivity between:

- Airflow workers → dbt target database
- Airflow → dbt project files
- Airflow → Kubernetes cluster (if using K8s tasks)

## Next Steps

With prerequisites in place:

- [Install dmp-af](installation.md)
- [Follow the Quick Start](quick-start.md)
- [Set up with Docker](docker-compose.md)
