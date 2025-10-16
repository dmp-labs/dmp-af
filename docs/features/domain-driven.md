# Domain-Driven Architecture

dmp-af is designed for domain-driven data architectures and data mesh.

## Overview

Models are automatically grouped into DAGs by domain, enabling:

- Parallel execution across domains
- Clear ownership boundaries
- Independent deployment cycles
- Scalable organization

## How It Works

Models are grouped by their dbt package/subdirectory:

```
models/
  svc_orders/     → svc_orders_daily DAG
  svc_customers/  → svc_customers_daily DAG
  dmn_analytics/  → dmn_analytics_daily DAG
```

## Benefits

- **Isolation**: Failures in one domain don't affect others
- **Parallelism**: Domains run simultaneously
- **Ownership**: Clear team boundaries
- **Scalability**: Add domains without DAG complexity

## Example

See [Advanced Project Tutorial](../tutorials/advanced-project.md) for a multi-domain setup.
