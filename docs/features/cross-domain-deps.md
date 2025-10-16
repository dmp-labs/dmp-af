# Cross-Domain Dependencies

Models in different domains can depend on each other seamlessly.

## Overview

dmp-af automatically creates ExternalTaskSensors for cross-DAG dependencies.

## How It Works

When a model in `domain_a` references a model in `domain_b`:

1. dmp-af detects the cross-domain reference
2. Creates an ExternalTaskSensor in domain_a's DAG
3. Waits for domain_b's task to complete
4. Then executes domain_a's model

## Example

```yaml
# Domain: svc_orders
models:
  - name: svc_orders.clean_orders
    config:
      schedule: "@daily"

# Domain: dmn_analytics
  - name: dmn_analytics.orders_report
    config:
      schedule: "@daily"
      dependencies:
        svc_orders.clean_orders:
          wait_policy: last
```

## Learn More

- [Dependencies Configuration](../configuration/dependencies.md)
- [Dependencies Tutorial](../tutorials/dependencies.md)

![Cross-Domain Dependencies](../static/cross_domain_dependencies.png)
