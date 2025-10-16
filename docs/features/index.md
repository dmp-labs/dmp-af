# Features

dmp-af provides powerful features for running dbt at scale on Airflow.

## Core Features

### [Domain-Driven Architecture](domain-driven.md)
Organize models by domain into separate DAGs for parallel execution and data mesh architectures.

### [Flexible Scheduling](scheduling.md)
Run models on different schedules: hourly, daily, weekly, monthly, or on-demand.

### [Distributed Runs](distributed-runs.md)
Each dbt model becomes an independent Airflow task while preserving dependencies.

### [Manual Run DAG](dbt-run-model-dag.md)
Manually trigger arbitrary dbt runs for backfills and testing.

## Advanced Features

### [Test Separation](tests-separation.md)
Separate small, medium, and large tests into different execution paths.

### [Cross-Domain Dependencies](cross-domain-deps.md)
Models in different domains and schedules can depend on each other seamlessly.

## Key Benefits

- **Auto-Generated DAGs**: No manual DAG writing required
- **Idempotent Runs**: Date intervals passed to every execution
- **Team-Friendly**: Analytics teams stay in dbt
- **Enterprise-Ready**: Multi-target, Kubernetes, and integration support
