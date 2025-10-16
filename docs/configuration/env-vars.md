# Environment Variables

Pass custom environment variables to dbt runs.

## Configuration

```yaml
models:
  - name: my_model
    config:
      env:
        MY_VAR: "value"
        AIRFLOW_VAR: "{{ var.value.get('my_var', 'default') }}"
```

## Airflow Template Rendering

Use Airflow variables and macros in environment variables.

## Related Topics

- [Model Configuration](model-config.md)
- [Advanced Configuration](advanced.md)
