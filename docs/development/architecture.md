# Architecture

Technical overview of dmp-af's architecture and design.

## Overview

dmp-af is a DAG compiler that transforms dbt manifest files into Airflow DAG definitions.

## Core Components

### 1. Manifest Parser

Reads dbt `manifest.json` and extracts:
- Model definitions
- Dependencies
- Configuration
- Metadata

### 2. DAG Compiler

Groups models by:
- Domain (dbt package/directory)
- Schedule (`@daily`, `@hourly`, etc.)

Creates one DAG per (domain, schedule) combination.

### 3. Task Generator

Converts each dbt model into an Airflow task:
- DbtRunOperator for standard models
- DbtTestOperator for tests
- ExternalTaskSensor for cross-DAG dependencies

### 4. Dependency Resolver

Builds task dependencies:
- Intra-DAG: Standard Airflow `>>`
- Cross-DAG: ExternalTaskSensor

## Data Flow

```
dbt project → dbt compile → manifest.json
                                ↓
                        dmp-af compiler
                                ↓
                    Airflow DAG definitions
                                ↓
                        Airflow scheduler
                                ↓
                        Task execution
```

## Key Design Decisions

### One Model = One Task

Each dbt model is a separate Airflow task for:
- Granular retries
- Parallel execution
- Better monitoring

### Domain-Driven DAGs

Models grouped by domain for:
- Isolation
- Ownership
- Scalability

### Schedule-Based Splitting

Multiple schedules create multiple DAGs to:
- Optimize execution timing
- Separate concerns
- Manage complexity

## Extension Points

dmp-af can be extended through:
- Custom operators
- Configuration hooks
- Post-processing callbacks

## Source Code Structure

```
dmp_af/
  ├── dags.py              # DAG compilation entry point
  ├── conf.py              # Configuration models
  ├── operators/           # Custom Airflow operators
  │   ├── run.py          # DbtRunOperator
  │   ├── test.py         # DbtTestOperator
  │   └── sensors.py      # Dependency sensors
  ├── parser/              # Manifest parsing
  └── utils/               # Utilities
```

## Performance Considerations

- Manifest parsing is cached
- DAG compilation is lazy
- Sensors use exponential backoff
- Pool-based concurrency control

## Future Architecture

See [GitHub Issues](https://github.com/dmp-labs/dmp-af/issues) for planned improvements.
