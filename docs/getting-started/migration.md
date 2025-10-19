# Migration Guide: dbt-af to dmp-af

This guide helps you migrate from the original [dbt-af](https://github.com/Toloka/dbt-af) project to dmp-af.

!!! info "Fork Information"
    **dmp-af** is a fork of dbt-af (version 0.14.6) with ongoing enhancements and modifications by `dmp-labs`. The core functionality remains the same, but package names and identifiers have been updated.

## Why Migrate?

- 🎯 Active maintenance and development
- 🎯 New features and improvements
- 🎯 Community-driven enhancements
- 🎯 Same Apache 2.0 license

## Migration Steps

### 1. Update Package Installation

Simply replace `dbt-af` with `dmp-af` in your dependencies:

=== "requirements.txt"
    ```diff
    - dbt-af
    + dmp-af
    ```

=== "pyproject.toml"
    ```diff
    [project]
    dependencies = [
    -   "dbt-af",
    +   "dmp-af",
    ]
    ```

=== "setup.py"
    ```diff
    install_requires=[
    -   "dbt-af",
    +   "dmp-af",
    ]
    ```

Then reinstall:

```bash
pip install -U dmp-af
```

### 2. Update Import Statements

Update the imports in your Airflow DAG files from `dbt_af` to `dmp_af`:

```diff
- from dbt_af.dags import compile_dbt_af_dags
- from dbt_af.conf import Config, DbtDefaultTargetsConfig, DbtProjectConfig
+ from dmp_af.dags import compile_dmp_af_dags
+ from dmp_af.conf import Config, DbtDefaultTargetsConfig, DbtProjectConfig
```

**Common imports to update:**

```diff
- from dbt_af.dags import compile_dbt_af_dags
+ from dmp_af.dags import compile_dmp_af_dags

- from dbt_af.conf import Config
+ from dmp_af.conf import Config

- from dbt_af.conf import DbtDefaultTargetsConfig
+ from dmp_af.conf import DbtDefaultTargetsConfig

- from dbt_af.conf import DbtProjectConfig
+ from dmp_af.conf import DbtProjectConfig
```

### 3. Update Function Calls

The main DAG compilation function has been renamed:

```diff
- dags = compile_dbt_af_dags(
+ dags = compile_dmp_af_dags(
      manifest_path='/path/to/manifest.json',
      config=config,
  )
```

### 4. Update Class Names

Several class names have been updated:

```diff
  # Graph builder
- from dbt_af.builder import DbtAfGraph
+ from dmp_af.builder import DmpAfGraph

  # Maintenance config
- from dbt_af.parser.dbt_node_model import DbtAFMaintenanceConfig
+ from dmp_af.parser.dbt_node_model import DmpAfMaintenanceConfig
```

### 5. Update Configuration Variables

If you have any custom configuration or variable names:

```diff
- dbt_af_config = Config(...)
- dbt_af_graph = DbtAfGraph.from_manifest(...)
+ dmp_af_config = Config(...)
+ dmp_af_graph = DmpAfGraph.from_manifest(...)
```

### 6. Update CLI Scripts

If you're using the manifest tests script:

```diff
- dbt-af-manifest-tests --manifest_path=./target/manifest.json
+ dmp-af-manifest-tests --manifest_path=./target/manifest.json
```

### 7. Update Documentation References

Update any documentation or comments in your codebase:

```diff
- # Using dbt-af for distributed dbt runs
- # See https://github.com/Toloka/dbt-af for details
+ # Using dmp-af for distributed dbt runs
+ # See https://github.com/dmp-labs/dmp-af for details
```

### 8. Update dbt Project Configuration

!!! success "No Changes Needed"
    Your `dbt_project.yml` configuration remains the same - no changes needed!

```yaml
# These settings work with both dbt-af and dmp-af
models:
  sql_cluster: "dev"
  daily_sql_cluster: "dev"
  py_cluster: "dev"
  bf_cluster: "dev"
```

## Testing Your Migration

After migrating, test that your DAGs are built correctly:

```bash
# Test your DAG file compiles successfully
python your_dmp_af_dag.py
```

If the script runs without errors, your DAGs are correctly configured.

### Verification Steps

1. **Check Airflow DAGs:**
    - Ensure DAGs appear in Airflow UI
    - Verify DAG structure looks correct
    - Test a sample DAG run

2. **Check Task Dependencies:**
    - Verify cross-domain dependencies are working
    - Check that tests are attached to correct models
    - Validate maintenance tasks are scheduled

3. **Run a Test DAG:**
    - Execute a small DAG to verify operators work correctly
    - Check logs for any errors or warnings

## Breaking Changes

### From dbt-af 0.14.6 to dmp-af

**Package Renaming:**

| Component | Old Name | New Name |
|-----------|----------|----------|
| Package name | `dbt-af` | `dmp-af` |
| Python module | `dbt_af` | `dmp_af` |
| Main function | `compile_dbt_af_dags()` | `compile_dmp_af_dags()` |
| Main class | `DbtAfGraph` | `DmpAfGraph` |
| Config class | `DbtAFMaintenanceConfig` | `DmpAfMaintenanceConfig` |

**Behavioral Changes:**

!!! success "No Breaking Changes"
    All functionality remains identical - only names have changed!

**Configuration Changes:**

!!! success "Fully Compatible"
    All configuration options remain the same - no changes needed!

**Version Numbering:**

- dmp-af continues version numbering from dbt-af (starting at 0.14.6+)

## Compatibility

- **Python**: 3.10, 3.11, 3.12
- **Airflow**: 2.6.3+, tested up to 2.11.0
- **dbt-core**: 1.7-1.10

## Migration Checklist

Use this checklist to ensure you've covered all migration steps:

- [x] Updated package in `requirements.txt` or `pyproject.toml`
- [x] Reinstalled with `pip install -U dmp-af`
- [x] Updated all `from dbt_af` imports to `from dmp_af`
- [x] Renamed `compile_dbt_af_dags()` to `compile_dmp_af_dags()`
- [x] Updated `DbtAfGraph` to `DmpAfGraph` (if used)
- [x] Updated `DbtAFMaintenanceConfig` to `DmpAfMaintenanceConfig` (if used)
- [x] Updated CLI script calls (if used)
- [x] Updated documentation and comments
- [x] Tested DAG compilation
- [x] Verified DAGs appear in Airflow UI
- [x] Ran test DAG execution

## Support

If you encounter issues during migration:

1. Check this guide for common scenarios
2. Review the [examples](https://github.com/dmp-labs/dmp-af/tree/main/examples) directory
3. Open an issue on [GitHub](https://github.com/dmp-labs/dmp-af/issues)

## Staying with dbt-af

If you prefer to stay with the original dbt-af:

- The original project is available at [github.com/Toloka/dbt-af](https://github.com/Toloka/dbt-af)
- You can continue using `dbt-af` without any changes
- Both projects share the same Apache 2.0 license

## Next Steps

After completing the migration:

- [x] Review the [Quick Start](quick-start.md) guide to explore dmp-af features
- [x] Check out [Tutorials](../tutorials/index.md) for practical examples
- [x] Read about [Configuration Options](../configuration/index.md)
- [x] Join the community on [GitHub](https://github.com/dmp-labs/dmp-af)
