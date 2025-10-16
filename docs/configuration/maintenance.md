# Maintenance Configuration

Configure TTL, data cleanup, and maintenance tasks.

## Overview

dmp-af supports automatic maintenance tasks for your data warehouse.

## TTL Configuration

```yaml
models:
  - name: events
    config:
      maintenance:
        ttl:
          key: created_at
          expiration_timeout: 90  # days
```

## Source Freshness

Check data freshness for sources.

## Related Topics

- [Maintenance Tutorial](../tutorials/maintenance.md)
- [Model Configuration](model-config.md)
