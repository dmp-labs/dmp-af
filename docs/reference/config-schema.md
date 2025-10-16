# Configuration Schema

Complete reference for all configuration options.

## Config

Top-level configuration object.

```python
from dmp_af.conf import Config

config = Config(
    dbt_project=DbtProjectConfig(...),
    dbt_default_targets=DbtDefaultTargetsConfig(...),
    dry_run=False,
    include_single_model_manual_dag=True,
)
```

## DbtProjectConfig

dbt project settings.

## DbtDefaultTargetsConfig

Default target configuration.

## Model Config Options

See [Model Configuration](../configuration/model-config.md) for complete list.

## Related

- [Configuration Overview](../configuration/index.md)
- [Advanced Configuration](../configuration/advanced.md)
