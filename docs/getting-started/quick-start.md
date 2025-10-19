# Quick Start

This guide walks you through creating your first dmp-af project from scratch using the included Jaffle Shop example.

## Overview

You'll learn how to:

1. Set up a local Airflow environment
2. Configure a dbt project for dmp-af
3. Generate Airflow DAGs from dbt models
4. Run and monitor distributed dbt tasks

## Step 1: Set Up Airflow

### Option A: Using Docker Compose (Recommended)

The easiest way to get started is with the provided Docker Compose setup.

First clone [dmp-af repository](https://github.com/dmp-labs/dmp-af)

```bash
git clone git@github.com:dmp-labs/dmp-af.git dmp-af
```

Navigate to `examples` directory:

```bash
cd dmp-af/examples
docker-compose up -d
```

This starts:

- Airflow webserver (http://localhost:8080)
- Airflow scheduler
- PostgreSQL database
- All required services

Default credentials: `airflow` / `airflow`

See [Docker Setup](docker-compose.md) for more details.

### Option B: Local Airflow Installation

If you prefer a local installation:

```bash
# Set Airflow home
export AIRFLOW_HOME=~/airflow

# Install Airflow
pip install apache-airflow==2.10.5

# Initialize database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# Start services
airflow webserver --port 8080 &
airflow scheduler &
```

## Step 2: Build the dbt manifest

Run the build script:

```bash
cd dags
./build_manifest.sh
```

This script:

1. Installs dbt dependencies
2. Compiles the Jaffle Shop projects
3. Generates `target/manifest.json`

All files are mounted to the Airflow container, so you can use them in the next step.

## Step 4: Configure Airflow Pools

dmp-af requires Airflow pools for task management:

```bash
airflow pools set dbt_dev 4 "Development pool"
airflow pools set dbt_sensor_pool 10 "Sensor pool"
```

Or use the Airflow UI:

1. Navigate to **Admin** → **Pools**
2. Create pools as shown above

## Step 5: Create Your DAG File

The example already includes a DAG file at `examples/dags/example_advanced_dmp_af_dag.py`.

Here's a simplified version to get started:

```python
# dags/my_first_dag.py
# LABELS: dag, airflow

from dmp_af.dags import compile_dmp_af_dags
from dmp_af.conf import Config, DbtDefaultTargetsConfig, DbtProjectConfig

# Configure your dbt project
config = Config(
    dbt_project=DbtProjectConfig(
        dbt_project_name='jaffle_shop',
        dbt_project_path='/path/to/examples/dags/jaffle_shop',
        dbt_models_path='/path/to/examples/dags/jaffle_shop/dbt/models',
        dbt_profiles_path='/path/to/examples/dags',
        dbt_target_path='/path/to/examples/dags/jaffle_shop/target',
        dbt_log_path='/path/to/examples/dags/jaffle_shop/logs',
        dbt_schema='jaffle_shop',
    ),
    dbt_default_targets=DbtDefaultTargetsConfig(default_target='dev'),
)

# Compile DAGs from manifest
dags = compile_dmp_af_dags(
    manifest_path='/path/to/examples/dags/jaffle_shop/target/manifest.json',
    config=config,
)

# Register with Airflow
for dag_name, dag in dags.items():
    globals()[dag_name] = dag
```

!!! tip "Update Paths"
    Replace `/path/to/` with the actual path to your dmp-af repository.

## Step 6: Verify DAGs in Airflow

1. Open Airflow UI: http://localhost:8080
2. Log in with your credentials
3. You should see DAGs like:
    * `svc_jaffle_shop_daily`
    * `svc_jaffle_shop_hourly`

![DAGs in Airflow](../static/svc_jaffle_shop_dags.png)

## Step 7: Run Your First DAG

1. Click on a DAG (e.g., `svc_jaffle_shop_daily`)
2. Enable the DAG using the toggle switch
3. Depending on `dry-run` argument from `compile_dmp_af_dags` function, you are going to see either running operations 
for the past day (dry_run is enabled) or backfilled runs up to configured dag start date (dry_run is disabled)
4. Watch tasks execute in the Graph or Grid view

![DAG Execution](../static/daily_basic_jaffle_shop_dag.png)

## Understanding the Generated DAGs

dmp-af automatically creates DAGs based on your dbt project structure:

### DAG Naming Convention

```
<domain>_<schedule>[_shift_<N>_<unit>]
```

Examples:

- `svc_jaffle_shop_daily` - Service domain, daily schedule
- `dmn_analytics_hourly` - Analytics domain, hourly schedule
- `svc_orders_daily_shift_1_hours` - Daily, shifted by 1 hour

### Task Structure

Each dbt model becomes an Airflow task:

```
<domain>.<layer>.<model_name>
```

For example:

- `svc_jaffle_shop.stg.orders` - Staging orders model
- `svc_jaffle_shop.ods.customers` - ODS customers model

## Exploring the Results

### View Task Logs

1. Click on any task in the DAG
2. Select "Log" to see dbt execution output
3. Check for SQL queries, row counts, and timing

### Check Database

If using the Docker setup, connect to Postgres:

```bash
docker exec -it postgres psql -U airflow -d airflow
```

```sql
\dt jaffle_shop.*
SELECT * FROM jaffle_shop.customers LIMIT 5;
```

## What's Next?

Now that you have your first DAGs running:

- **[Basic Project Tutorial](../tutorials/basic-project.md)** - Deep dive into project structure
- **[Advanced Project](../tutorials/advanced-project.md)** - Multiple domains and targets
- **[Configuration](../configuration/index.md)** - Customize your setup
- **[Features](../features/index.md)** - Explore advanced capabilities

## Troubleshooting

### DAGs Not Appearing

1. Check DAG file location is in Airflow's `dags_folder`
2. Verify no Python syntax errors: `python dags/my_first_dag.py`
3. Check Airflow logs: `airflow dags list-import-errors`

### Pool Errors

If you see pool-related errors:

```bash
airflow pools list
airflow pools set dbt_dev 4 "Dev pool"
```

### Import Errors

Ensure dmp-af is installed in the same environment as Airflow:

```bash
python -c "import dmp_af; print(dmp_af.__version__)"
```

### Manifest Not Found

Verify the manifest path exists and is readable:

```bash
ls -l /path/to/manifest.json
```

Recompile if needed:

```bash
cd /path/to/dbt/project
dbt compile --target dev
```
