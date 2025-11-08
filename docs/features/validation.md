# Validation Framework

dmp-af includes an extensible validation framework to catch configuration issues in your dbt project before they cause Airflow DAG failures.

## Overview

The validation framework runs rules against your dbt manifest to detect:

- **Configuration errors**: Invalid schedules, missing required fields, naming violations
- **Runtime issues**: Task names exceeding Airflow limits, missing dependencies
- **Best practices**: Source freshness, snapshot config, test coverage

Validations run independently of Airflow - no deployment needed to catch issues.

## Quick Start

```bash
# Basic validation
dmp-af validate \
  --manifest-path target/manifest.json \
  --profiles-path profiles.yml \
  --dbt-project-path dbt_project.yml \
  --models-path models \
  --target dev

# Or use directories (automatically finds manifest.json, profiles.yml, etc.)
dmp-af validate \
  --manifest-path target \
  --profiles-path . \
  --dbt-project-path . \
  --models-path models \
  --target dev
```

## CLI Options

### Required Arguments

- `--manifest-path`: Path to `manifest.json` or directory containing it
- `--profiles-path`: Path to `profiles.yml` or directory containing it
- `--dbt-project-path`: Path to `dbt_project.yml` or directory containing it
- `--models-path`: Path to dbt models directory
- `--target`: dbt target name (default: `dev`)

### Optional Arguments

```bash
# Run specific rules only
--rules conventional_model_name,airflow_task_name_length

# Exclude specific rules
--exclude-rules source_freshness_config,snapshot_strategy_config

# Load custom validators
--custom-rules-path /path/to/validators

# Treat warnings as errors
--warnings-as-errors

# Verbose logging
--verbose
```

## Output Format

```
=== Validation Results ===

❌ ERROR [conventional_model_name] Model name mismatch
   File: svc_jaffle_shop/customers.sql
   Expected FQN: svc_jaffle_shop.customers.customers
   Actual FQN:   customers
   Suggestion: Rename model to match folder structure

⚠️  WARNING [source_freshness_config] Source missing freshness config
   Source: raw.customers
   Suggestion: Add freshness config to dbt source definition

=== Summary ===
Total: 14 violations (8 errors, 6 warnings)
```

**Exit codes:**

- `0`: No violations or only warnings (when `--warnings-as-errors` not set)
- `1`: Errors found or warnings with `--warnings-as-errors`

## Built-in Validators

### Model Validators (run per dbt node)

**`conventional_model_name`** (ERROR)
Ensures model names match folder structure.

```yaml
# Example violation:
# File: finance/revenue.sql
# Model name: revenue_model  ❌
# Expected: finance.revenue
```

**`airflow_task_name_length`** (ERROR)
Validates Airflow task names ≤250 chars. Model dependency wait tasks reserve 5 chars for suffix pattern `__{dep_number}`.

```python
# Checks:
# - Model dep wait tasks: ≤245 chars
# - Test dep wait tasks: ≤250 chars
```

**`source_freshness_config`** (WARNING)
Checks dbt sources have freshness configuration.

```yaml
# Good:
sources:
  - name: raw
    tables:
      - name: customers
        freshness:
          warn_after: {count: 12, period: hour}
```

**`snapshot_strategy_config`** (ERROR)
Validates snapshots have required config (strategy, unique_key, updated_at).

```sql
-- snapshots/orders_snapshot.sql
{{ config(
    strategy='timestamp',
    unique_key='id',
    updated_at='updated_at'
) }}
```

**`valid_schedule_format`** (ERROR)
Ensures schedule is valid cron or preset (`@daily`, `@hourly`, etc.).

```yaml
# dbt model config
meta:
  dmp_af:
    schedule: "@daily"  # Valid
    # schedule: "invalid" ❌
```

**`parseable_dbt_nodes`** (ERROR)
Smoke test - ensures all manifest nodes parse into DbtNode objects.

### Project Validators (validate project-level data)

These validators check project-wide concerns that require accessing multiple nodes or cross-cutting data, rather than validating individual models.

**`unique_test_names`** (ERROR)
Validates all dbt test names are unique across project.

```yaml
# Violation example:
# - tests/finance/test_revenue_positive.sql
# - tests/marketing/test_revenue_positive.sql
# Both named: test_revenue_positive ❌
```

**`medium_test_parents`** (ERROR)
Ensures medium tests have parent nodes in graph.

**`models_in_dags`** (ERROR)
Validates all dbt models from manifest appear in generated Airflow DAGs.

**`kubernetes_profile_fields`** (ERROR)
Checks Kubernetes profiles have required fields (namespace, image, etc.).

```yaml
# profiles.yml
your_profile:
  outputs:
    dev:
      type: duckdb
      meta:
        kubernetes:
          namespace: airflow
          image: my-dbt:latest
          service_account_name: dbt-runner
```

## Custom Validators

Create custom validators by inheriting base classes:

### Model Validator (runs per dbt node)

```python
# my_validators/check_owner.py
from dmp_af.validation import BaseModelValidator, RuleViolation, Severity, ValidationContext
from dmp_af.parser.dbt_node_model import DbtNode

class OwnerValidator(BaseModelValidator):
    """Ensure all models have owner tag."""

    name = 'owner_required'
    description = 'All models must have owner tag'
    severity = Severity.ERROR  # Optional, defaults to ERROR

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        if not model.is_model():
            return []

        owner = model.config.tags.get('owner')
        if not owner:
            return [RuleViolation(
                rule_name=self.name,
                message=f'Model missing owner tag',
                node_id=model.unique_id,
                severity=self.severity,
                suggestion='Add owner tag in dbt model config'
            )]
        return []
```

### Project Validator (runs once)

```python
# my_validators/check_test_coverage.py
from dmp_af.validation import BaseProjectValidator, RuleViolation, Severity, ValidationContext

class TestCoverageValidator(BaseProjectValidator):
    """Ensure test coverage >80%."""

    name = 'test_coverage'
    description = 'Test coverage must exceed 80%'
    needs_graph = True  # Triggers lazy graph loading

    def validate(self, context: ValidationContext) -> list[RuleViolation]:
        models = [n for n in context.graph.dbt_nodes if n.is_model()]
        tests = [n for n in context.graph.dbt_nodes if n.is_test()]

        coverage = len(tests) / len(models) if models else 0

        if coverage < 0.8:
            return [RuleViolation(
                rule_name=self.name,
                message=f'Test coverage {coverage:.1%} below 80% threshold',
                severity=Severity.WARNING,
                suggestion=f'Add {int((0.8 - coverage) * len(models))} more tests'
            )]
        return []
```

### Using Custom Validators

```bash
dmp-af validate \
  --manifest-path target/manifest.json \
  --profiles-path profiles.yml \
  --dbt-project-path dbt_project.yml \
  --models-path models \
  --custom-rules-path ./my_validators \
  --target dev
```

**WARNING**: Custom validators execute arbitrary Python code. Only load validators you trust.

## API Reference

### Base Classes

```python
from dmp_af.validation import (
    BaseModelValidator,     # Per-node validation
    BaseProjectValidator,   # Project-wide validation
    RuleViolation,          # Violation model
    Severity,               # ERROR or WARNING
    ValidationContext,      # Context with manifest, profiles, config
)
```

### BaseModelValidator

```python
class BaseModelValidator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Validator name (required)."""

    @property
    def description(self) -> str:
        """Validator description (optional, default: '')."""

    @property
    def severity(self) -> Severity:
        """Severity level (optional, default: Severity.ERROR)."""

    @abstractmethod
    def validate(
        self,
        model: DbtNode,
        context: ValidationContext
    ) -> list[RuleViolation]:
        """Validate single dbt node."""
```

Override with class attributes:

```python
class MyValidator(BaseModelValidator):
    name = 'my_validator'  # Required
    description = 'My description'  # Optional
    severity = Severity.WARNING  # Optional

    def validate(self, model, context):
        ...
```

### BaseProjectValidator

```python
class BaseProjectValidator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Validator name (required)."""

    @property
    def description(self) -> str:
        """Validator description (optional, default: '')."""

    @property
    def severity(self) -> Severity:
        """Severity level (optional, default: Severity.ERROR)."""

    @property
    def needs_graph(self) -> bool:
        """Whether validator needs DmpAfGraph (optional, default: False)."""

    @abstractmethod
    def validate(
        self,
        context: ValidationContext
    ) -> list[RuleViolation]:
        """Validate entire project."""
```

### ValidationContext

```python
@attrs.define
class ValidationContext:
    manifest: dict          # Parsed manifest.json
    profiles: dict          # Parsed profiles.yml
    dbt_project: dict       # Parsed dbt_project.yml
    config: Config          # dmp-af Config object

    @property
    def graph(self) -> DmpAfGraph:
        """Lazy-loaded DmpAfGraph (only if validators need it)."""
```

Access raw manifest data:

```python
def validate(self, model: DbtNode, context: ValidationContext):
    # Get raw node dict
    node_dict = context.manifest['nodes'].get(model.unique_id)

    # Access depends_on (not in DbtNode)
    deps = node_dict.get('depends_on', {}).get('nodes', [])

    # Access raw/compiled SQL (provided as-is, not parsed)
    raw_sql = node_dict.get('raw_code', '')
    compiled_sql = node_dict.get('compiled_code', '')
```

**Note**: dmp-af provides SQL code as-is without parsing. For SQL parsing and analysis, use [sqlglot](https://github.com/tobymao/sqlglot).

### RuleViolation

```python
@attrs.define(frozen=True)
class RuleViolation:
    rule_name: str          # Validator name
    message: str            # Violation description
    severity: Severity      # ERROR or WARNING
    node_id: str | None     # dbt node unique_id (optional)
    suggestion: str | None  # Fix suggestion (optional)
```

### Severity Enum

```python
class Severity(str, Enum):
    ERROR = 'error'    # Blocking, causes exit code 1
    WARNING = 'warning'  # Non-blocking (unless --warnings-as-errors)
```

## Architecture

### Execution Flow

1. **Load artifacts**: Parse manifest.json, profiles.yml, dbt_project.yml
2. **Build context**: Create ValidationContext with loaded data
3. **Load validators**: Discover built-in + custom validators from folder
4. **Filter**: Apply `--rules` and `--exclude-rules`
5. **Run model validators**: Iterate all manifest nodes, call each validator
6. **Lazy-load graph**: Only if project validators set `needs_graph=True`
7. **Run project validators**: Call each once with full context
8. **Format output**: Pretty-print violations with emoji indicators
9. **Exit**: Code 0 (clean) or 1 (violations)

### Performance Optimization

**Lazy graph loading**: The expensive DmpAfGraph is only loaded if validators need it via `needs_graph=True`.

```python
# Fast - no graph loading
class QuickValidator(BaseModelValidator):
    name = 'quick'

    def validate(self, model, context):
        return []

# Slow - triggers graph load
class SlowValidator(BaseProjectValidator):
    name = 'slow'
    needs_graph = True  # Loads graph before running

    def validate(self, context):
        # context.graph now available
        for node in context.graph.dbt_nodes:
            ...
```

For 2000+ model projects, avoiding graph load saves ~10-30s.

### Auto-discovery

Custom validators are auto-discovered by:

1. Scanning folder for `*.py` files (skips `_*.py`)
2. Importing module with `importlib.util`
3. Finding classes that inherit `BaseModelValidator` or `BaseProjectValidator`
4. Instantiating (Python ABC enforces required fields)
5. Adding to validator list

No registration or config needed - just create file in folder.

### Fault Tolerance

Broken validators don't crash validation:

```python
# Bad validator (missing name)
class BrokenValidator(BaseModelValidator):
    def validate(self, model, context):
        return []

# Logged but doesn't crash:
# ERROR: Failed to load validator BrokenValidator:
#        Can't instantiate abstract class with abstract method 'name'
```

Unparseable nodes are skipped with debug logging:

```python
# Skipped with: DEBUG: Skipping unparseable node model.x: KeyError('name')
```

## Integration with CI/CD

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: dmp-af-validate
        name: dmp-af validation
        entry: dmp-af validate
        args:
          - --manifest-path=target
          - --profiles-path=.
          - --dbt-project-path=.
          - --models-path=models
          - --target=dev
        language: system
        pass_filenames: false
```

### GitHub Actions

```yaml
# .github/workflows/validate.yml
name: Validate dbt
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dmp-af
        run: pip install dmp-af

      - name: Compile dbt
        run: dbt compile --target dev

      - name: Run validation
        run: |
          dmp-af validate \
            --manifest-path target \
            --profiles-path . \
            --dbt-project-path . \
            --models-path models \
            --target dev \
            --warnings-as-errors
```

## Best Practices

### 1. Run Early and Often

```bash
# After dbt changes
dbt compile && dmp-af validate ...

# In CI/CD pipeline
# In pre-commit hooks
```

### 2. Use Warnings for Soft Rules

```python
class StyleGuideValidator(BaseModelValidator):
    name = 'style_guide'
    severity = Severity.WARNING  # Don't block builds
```

### 3. Provide Actionable Suggestions

```python
return [RuleViolation(
    rule_name=self.name,
    message='Model missing description',
    node_id=model.unique_id,
    severity=self.severity,
    suggestion='Add description in dbt model config or schema.yml'  # ✅
    # suggestion='Fix it'  # ❌ Not actionable
)]
```

### 4. Skip Irrelevant Nodes Early

```python
def validate(self, model: DbtNode, context: ValidationContext):
    if not model.is_model():
        return []  # Skip tests, sources, etc.

    # Model-specific validation
    ...
```

### 5. Use Context for Raw Data

```python
def validate(self, model: DbtNode, context: ValidationContext):
    # DbtNode doesn't have depends_on
    node_dict = context.manifest['nodes'].get(model.unique_id)
    deps = node_dict.get('depends_on', {}).get('nodes', [])
```

### 6. Set `needs_graph` Appropriately

```python
# Only set needs_graph=True if you actually use context.graph
class GraphValidator(BaseProjectValidator):
    needs_graph = True  # Loads expensive graph

    def validate(self, context):
        for node in context.graph.dbt_nodes:  # Uses graph
            ...
```

### 7. Test Validators with Real Manifests

```python
# tests/validation/test_my_validator.py
def test_owner_validator(validation_context):
    validator = OwnerValidator()

    # Create test node
    node = DbtNode(
        unique_id='model.proj.test',
        name='test',
        resource_type='model',
        config={'tags': {}},  # Missing owner
        ...
    )

    violations = validator.validate(node, validation_context)
    assert len(violations) == 1
    assert violations[0].rule_name == 'owner_required'
```

## Troubleshooting

### "Can't instantiate abstract class"

```
ERROR: Failed to load validator MyValidator:
       Can't instantiate abstract class MyValidator with abstract method 'name'
```

**Fix**: Add required `name` field:

```python
class MyValidator(BaseModelValidator):
    name = 'my_validator'  # Required!
```

### "Module not found" when loading custom validators

```
ERROR: Failed to load validator from my_validators/check.py: No module named 'dmp_af'
```

**Fix**: Install dmp-af in same environment:

```bash
pip install dmp-af
# or
uv pip install dmp-af
```

### No violations found but expecting some

1. Check rule is running: `--verbose` shows loaded validators
2. Verify manifest is up-to-date: `dbt compile`
3. Check rule filtering: remove `--rules` flag
4. Add debug prints in custom validator

### Performance issues with large projects

1. Avoid `needs_graph=True` if not needed
2. Use model validators (iterate efficiently) over project validators (manual iteration)
3. Profile with `--verbose` to see load times

## Migration from pytest-based tests

Old approach:

```python
# dmp_af_functional_tests/test_naming.py
def test_naming_convention(manifest):
    for node in manifest['nodes'].values():
        assert check_naming(node)
```

New approach:

```python
# my_validators/naming.py
class NamingValidator(BaseModelValidator):
    name = 'naming_convention'

    def validate(self, model, context):
        if not check_naming(model):
            return [RuleViolation(...)]
        return []
```

Benefits:
- No pytest dependency
- Standalone CLI tool
- User-extensible
- Better output formatting
- Severity levels (error vs warning)

## Related Documentation

- [CLI Reference](../reference/cli.md)
- [Testing Guide](../development/testing.md)
- [Architecture](../development/architecture.md)
