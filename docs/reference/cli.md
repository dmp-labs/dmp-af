# CLI Commands

Command-line tools for dmp-af.

## dmp-af validate

**Recommended**: Validate dbt project configuration and catch issues before deployment.

```bash
dmp-af validate \
  --manifest-path target/manifest.json \
  --profiles-path profiles.yml \
  --dbt-project-path dbt_project.yml \
  --models-path models \
  --target dev
```

### Required Arguments

| Argument | Description |
|----------|-------------|
| `--manifest-path` | Path to `manifest.json` or directory containing it |
| `--profiles-path` | Path to `profiles.yml` or directory containing it |
| `--dbt-project-path` | Path to `dbt_project.yml` or directory containing it |
| `--models-path` | Path to dbt models directory |
| `--target` | dbt target name (default: `dev`) |

### Optional Arguments

| Argument | Description |
|----------|-------------|
| `--custom-rules-path` | Path to custom validators folder |
| `--rules` | Comma-separated rule names to run (runs all if not specified) |
| `--exclude-rules` | Comma-separated rule names to exclude |
| `--warnings-as-errors` | Treat warnings as errors (exit code 1) |
| `--verbose`, `-v` | Enable verbose logging |

### Examples

```bash
# Basic validation
dmp-af validate \
  --manifest-path target \
  --profiles-path . \
  --dbt-project-path . \
  --models-path models \
  --target dev

# Run specific rules only
dmp-af validate \
  --manifest-path target \
  --profiles-path . \
  --dbt-project-path . \
  --models-path models \
  --rules conventional_model_name,airflow_task_name_length

# Exclude specific rules
dmp-af validate \
  --manifest-path target \
  --profiles-path . \
  --dbt-project-path . \
  --models-path models \
  --exclude-rules source_freshness_config

# Load custom validators
dmp-af validate \
  --manifest-path target \
  --profiles-path . \
  --dbt-project-path . \
  --models-path models \
  --custom-rules-path ./validators

# Verbose output with warnings as errors
dmp-af validate \
  --manifest-path target \
  --profiles-path . \
  --dbt-project-path . \
  --models-path models \
  --warnings-as-errors \
  --verbose
```

### Exit Codes

- `0`: No violations or only warnings (when `--warnings-as-errors` not set)
- `1`: Errors found or warnings with `--warnings-as-errors`

See [Validation Framework](../features/validation.md) for detailed documentation.

## dmp-af-manifest-tests

**Deprecated**: Use `dmp-af validate` instead.

Legacy alias for validation command.

```bash
dmp-af-manifest-tests --help
```

## mini_dbt_project_generator

Generate minimal dbt projects for testing.

```bash
mini_dbt_project_generator --help
```

## Related

- [Validation Framework](../features/validation.md)
- [Testing](../development/testing.md)
- [Contributing](../development/contributing.md)
