# Operators

Airflow operators used by dmp-af.

## DbtRunOperator

Executes `dbt run` for a single model.

## DbtTestOperator

Executes `dbt test` for a model or test.

## DbtSensor

Waits for upstream dbt tasks.

## KubernetesPodOperator

For Kubernetes-based execution.

## Related

- [Kubernetes Tutorial](../tutorials/kubernetes.md)
- [Python Venv Tutorial](../tutorials/python-venv.md)
