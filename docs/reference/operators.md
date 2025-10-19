# Operators

Airflow operators used by dmp-af.

## DbtRunOperator

Executes `dbt run` for a single model.

### Automatic Variable Injection

Every DbtRunOperator automatically receives time interval variables passed via `--vars`:

- `start_dttm`: Processing interval start (ISO 8601)
- `end_dttm`: Processing interval end (ISO 8601)
- `overlap`: Boolean flag for overlapping intervals

These variables are automatically calculated based on:
1. User-defined parameters (from DAG run configuration)
2. Manual trigger behavior (full day processing)
3. Scheduled run intervals (from Airflow's `data_interval_start`/`data_interval_end`)

See [Distributed Runs - Time Interval Variables](../features/distributed-runs.md#time-interval-variables) for detailed logic.

### Base Implementation

All model-running operators inherit from `DbtIntervalActionOperator`, which:

1. Extracts time interval from Airflow context
2. Converts to dbt-compatible variable format
3. Passes to dbt via `--vars` flag as JSON
4. Isolates manifest.json in temporary directory

### Configuration

Operators support:
- Custom target environments
- Pool-based resource management
- Configurable retry policies
- Debug mode
- Custom environment variables

## DbtTestOperator

Executes `dbt test` for a model or test.

Inherits the same time interval logic as DbtRunOperator, allowing tests to access `start_dttm` and `end_dttm` variables.

## DbtSnapshotOperator

Executes `dbt snapshot` for snapshot models.

Like other operators, receives automatic time interval variables for snapshot processing.

## DbtSensor

Waits for upstream dbt tasks.

Used for cross-domain dependencies. Does not execute dbt commands but coordinates task execution across different DAGs.

## KubernetesPodOperator

For Kubernetes-based execution.

When configured, dmp-af wraps dbt commands in Kubernetes pods, maintaining the same variable injection logic.

## Python Virtualenv Operator

For isolated Python environment execution.

Alternative to Kubernetes when you need environment isolation but don't use K8s infrastructure.

## Related

- [Distributed Runs - Time Intervals](../features/distributed-runs.md#time-interval-variables)
- [Kubernetes Tutorial](../tutorials/kubernetes.md)
- [Python Venv Tutorial](../tutorials/python-venv.md)
- [Model Configuration](../configuration/model-config.md)
