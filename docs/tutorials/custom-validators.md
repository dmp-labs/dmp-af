# Custom Validators Tutorial

Learn how to create custom validation rules for your dbt project using dmp-af's extensible validation framework.

## Prerequisites

- dmp-af installed
- dbt project with compiled manifest
- Basic Python knowledge

## Tutorial Overview

We'll build three custom validators:

1. **Owner Tag Validator** (Model) - Ensure all models have an owner tag
2. **Test Coverage Validator** (Project) - Enforce minimum test coverage
3. **Materialization Validator** (Model) - Warn about expensive materializations

## Setup

Create a validators directory:

```bash
mkdir -p validators
cd validators
```

## Example 1: Owner Tag Validator

Models without owners are hard to maintain. Let's enforce ownership.

### Create the Validator

```python
# validators/owner_validator.py
from dmp_af.validation import (
    BaseModelValidator,
    RuleViolation,
    Severity,
    ValidationContext
)
from dmp_af.parser.dbt_node_model import DbtNode


class OwnerTagValidator(BaseModelValidator):
    """Ensure all production models have an owner tag."""

    name = 'owner_tag_required'
    description = 'Production models must have owner tag'

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        # Only check models
        if not model.is_model():
            return []

        # Skip dev/test models
        if 'dev' in model.config.tags or 'test' in model.config.tags:
            return []

        # Check for owner tag
        owner = model.config.tags.get('owner')
        if not owner:
            return [RuleViolation(
                rule_name=self.name,
                message='Production model missing owner tag',
                node_id=model.unique_id,
                severity=self.severity,
                suggestion=(
                    'Add owner tag in dbt model config:\n'
                    '  {{ config(tags=["owner:team_name"]) }}'
                )
            )]

        return []
```

### Test It

```bash
# Run validation with custom validator
dmp-af validate \
  --manifest-path target \
  --profiles-path . \
  --dbt-project-path . \
  --models-path ./models \
  --custom-rules-path . \
  --target dev
```

### Expected Output

```
❌ ERROR [owner_tag_required] Production model missing owner tag
   Node: model.jaffle_shop.customers
   Suggestion: Add owner tag in dbt model config:
     {{ config(tags=["owner:team_name"]) }}
```

### Fix the Violation

```sql
-- models/customers.sql
{{ config(
    tags=["owner:analytics_team"]
) }}

select * from {{ ref('raw_customers') }}
```

## Example 2: Test Coverage Validator

Enforce minimum test coverage across your project.

### Create the Validator

```python
# validators/test_coverage_validator.py
from dmp_af.validation import (
    BaseProjectValidator,
    RuleViolation,
    Severity,
    ValidationContext
)


class TestCoverageValidator(BaseProjectValidator):
    """Ensure minimum test coverage across project."""

    name = 'test_coverage'
    description = 'Test coverage must meet threshold'
    severity = Severity.WARNING  # Non-blocking
    needs_graph = True  # Requires graph access

    COVERAGE_THRESHOLD = 0.8  # 80%

    def validate(self, context: ValidationContext) -> list[RuleViolation]:
        # Count models and tests
        models = [n for n in context.graph.dbt_nodes if n.is_model()]
        tests = [n for n in context.graph.dbt_nodes if n.is_test()]

        if not models:
            return []

        # Calculate coverage (tests per model)
        coverage = len(tests) / len(models)

        if coverage < self.COVERAGE_THRESHOLD:
            tests_needed = int((self.COVERAGE_THRESHOLD - coverage) * len(models))

            return [RuleViolation(
                rule_name=self.name,
                message=(
                    f'Test coverage {coverage:.1%} below '
                    f'{self.COVERAGE_THRESHOLD:.0%} threshold'
                ),
                severity=self.severity,
                suggestion=(
                    f'Add approximately {tests_needed} more tests. '
                    f'Current: {len(tests)} tests for {len(models)} models'
                )
            )]

        return []
```

### Test It

```bash
dmp-af validate \
  --manifest-path target \
  --profiles-path . \
  --dbt-project-path . \
  --models-path ./models \
  --custom-rules-path . \
  --target dev
```

### Expected Output

```
⚠️  WARNING [test_coverage] Test coverage 45% below 80% threshold
   Suggestion: Add approximately 15 more tests. Current: 20 tests for 45 models
```

## Example 3: Materialization Validator

Warn about expensive table materializations that could use incremental.

### Create the Validator

```python
# validators/materialization_validator.py
from dmp_af.validation import (
    BaseModelValidator,
    RuleViolation,
    Severity,
    ValidationContext
)
from dmp_af.parser.dbt_node_model import DbtNode


class MaterializationValidator(BaseModelValidator):
    """Warn about expensive table materializations."""

    name = 'expensive_materialization'
    description = 'Large tables should use incremental materialization'
    severity = Severity.WARNING

    # Threshold for suggesting incremental (lines of SQL)
    LARGE_MODEL_LINES = 100

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        if not model.is_model():
            return []

        # Check materialization
        materialization = model.config.materialized
        if materialization in ('incremental', 'view', 'ephemeral'):
            return []  # These are fine

        # Check model size (rough heuristic)
        node_dict = context.manifest['nodes'].get(model.unique_id)
        if not node_dict:
            return []

        # Count lines in raw SQL (simple heuristic)
        # For advanced SQL analysis, use sqlglot
        raw_sql = node_dict.get('raw_code', '')
        line_count = len(raw_sql.splitlines())

        if line_count > self.LARGE_MODEL_LINES:
            return [RuleViolation(
                rule_name=self.name,
                message=(
                    f'Large model ({line_count} lines) using '
                    f'{materialization} materialization'
                ),
                node_id=model.unique_id,
                severity=self.severity,
                suggestion=(
                    'Consider incremental materialization for large models:\n'
                    '  {{ config(materialized="incremental") }}'
                )
            )]

        return []
```

### Test It

```bash
dmp-af validate \
  --manifest-path target \
  --profiles-path . \
  --dbt-project-path . \
  --models-path ./models \
  --custom-rules-path . \
  --rules expensive_materialization  # Run only this rule
```

## Advanced Patterns

### Pattern 1: Accessing Raw Manifest Data

DbtNode doesn't have all manifest fields. Access raw data via context:

```python
def validate(self, model: DbtNode, context: ValidationContext):
    # Get raw node
    node_dict = context.manifest['nodes'].get(model.unique_id)

    # Access fields not in DbtNode
    depends_on = node_dict.get('depends_on', {}).get('nodes', [])
    columns = node_dict.get('columns', {})

    # Access raw/compiled SQL (provided as-is, not parsed)
    # For SQL parsing/analysis, use sqlglot
    raw_sql = node_dict.get('raw_code', '')
    compiled_sql = node_dict.get('compiled_code', '')
```

**Note**: dmp-af provides SQL code as-is without parsing. For SQL parsing and analysis, use [sqlglot](https://github.com/tobymao/sqlglot).

### Pattern 2: Domain-Specific Validation

```python
class FinanceDomainValidator(BaseModelValidator):
    """Finance domain models require specific tags."""

    name = 'finance_domain_rules'

    def validate(self, model: DbtNode, context: ValidationContext):
        # Check if model in finance domain
        if 'finance' not in model.fqn:
            return []  # Skip non-finance models

        # Finance-specific checks
        violations = []

        # Must have PII tag
        if 'pii' not in model.config.tags and 'no_pii' not in model.config.tags:
            violations.append(RuleViolation(
                rule_name=self.name,
                message='Finance models must have PII classification tag',
                node_id=model.unique_id,
                severity=Severity.ERROR,
                suggestion='Add tag: pii or no_pii'
            ))

        # Must have retention tag
        retention_tags = [t for t in model.config.tags if t.startswith('retention:')]
        if not retention_tags:
            violations.append(RuleViolation(
                rule_name=self.name,
                message='Finance models must have retention policy tag',
                node_id=model.unique_id,
                severity=Severity.ERROR,
                suggestion='Add tag: retention:7y (or appropriate period)'
            ))

        return violations
```

### Pattern 3: Cross-Model Dependencies

```python
class DependencyValidator(BaseModelValidator):
    """Validate cross-domain dependencies follow rules."""

    name = 'dependency_rules'
    needs_graph = False  # Can use manifest directly

    def validate(self, model: DbtNode, context: ValidationContext):
        if not model.is_model():
            return []

        node_dict = context.manifest['nodes'].get(model.unique_id)
        depends_on = node_dict.get('depends_on', {}).get('nodes', [])

        violations = []
        model_domain = model.fqn[0]  # First part of FQN is domain

        for dep_id in depends_on:
            if not dep_id.startswith('model.'):
                continue  # Skip sources, etc.

            dep_dict = context.manifest['nodes'].get(dep_id)
            if not dep_dict:
                continue

            # Extract dep domain
            dep_fqn = dep_dict.get('fqn', [])
            dep_domain = dep_fqn[0] if dep_fqn else None

            # Rule: staging can't depend on marts
            if model_domain == 'staging' and dep_domain == 'marts':
                violations.append(RuleViolation(
                    rule_name=self.name,
                    message=f'Staging model depends on mart: {dep_dict["name"]}',
                    node_id=model.unique_id,
                    severity=Severity.ERROR,
                    suggestion='Staging should only depend on raw/staging layers'
                ))

        return violations
```

### Pattern 4: Config-Based Severity

```python
class ConfigurableValidator(BaseModelValidator):
    """Validator with configurable thresholds."""

    name = 'configurable'

    def __init__(self, max_columns: int = 50, severity: Severity = Severity.WARNING):
        self.max_columns = max_columns
        self._severity = severity

    @property
    def severity(self) -> Severity:
        return self._severity

    def validate(self, model: DbtNode, context: ValidationContext):
        if not model.is_model():
            return []

        node_dict = context.manifest['nodes'].get(model.unique_id)
        columns = node_dict.get('columns', {})

        if len(columns) > self.max_columns:
            return [RuleViolation(
                rule_name=self.name,
                message=f'Model has {len(columns)} columns (max: {self.max_columns})',
                node_id=model.unique_id,
                severity=self.severity,
                suggestion='Consider splitting into multiple models'
            )]

        return []
```

## Testing Custom Validators

Create tests for your validators:

```python
# tests/test_owner_validator.py
import pytest
from dmp_af.validation import ValidationContext
from dmp_af.parser.dbt_node_model import DbtNode
from validators.owner_validator import OwnerTagValidator


def test_owner_validator_missing_tag():
    """Test that validator catches missing owner tag."""

    validator = OwnerTagValidator()

    # Create test node without owner
    node = DbtNode(
        unique_id='model.proj.test',
        name='test',
        resource_type='model',
        fqn=['proj', 'test'],
        config={'tags': {}},
        depends_on={'nodes': []},
    )

    # Mock context (only need node)
    context = None  # Not used in this validator

    violations = validator.validate(node, context)

    assert len(violations) == 1
    assert violations[0].rule_name == 'owner_tag_required'
    assert 'owner tag' in violations[0].message.lower()


def test_owner_validator_with_tag():
    """Test that validator passes when owner tag present."""

    validator = OwnerTagValidator()

    node = DbtNode(
        unique_id='model.proj.test',
        name='test',
        resource_type='model',
        fqn=['proj', 'test'],
        config={'tags': {'owner': 'analytics_team'}},
        depends_on={'nodes': []},
    )

    context = None
    violations = validator.validate(node, context)

    assert len(violations) == 0
```

Run tests:

```bash
pytest tests/test_owner_validator.py -v
```

## Integration with CI/CD

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: dmp-af-validate-custom
        name: dmp-af custom validation
        entry: dmp-af validate
        args:
          - --manifest-path=target
          - --profiles-path=.
          - --dbt-project-path=.
          - --models-path=models
          - --custom-rules-path=validators
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

      - name: Install dependencies
        run: |
          pip install dmp-af
          pip install dbt-core dbt-duckdb

      - name: Compile dbt
        run: dbt compile --target dev

      - name: Run validation
        run: |
          dmp-af validate \
            --manifest-path target \
            --profiles-path . \
            --dbt-project-path . \
            --models-path models \
            --custom-rules-path validators \
            --target dev
```

## Best Practices

### 1. Start with Warnings

```python
severity = Severity.WARNING  # Don't block builds initially
```

Promote to ERROR once team is compliant.

### 2. Provide Actionable Suggestions

```python
# Good ✅
suggestion='Add tag in config: {{ config(tags=["owner:team"]) }}'

# Bad ❌
suggestion='Fix the tag'
```

### 3. Skip Irrelevant Nodes

```python
def validate(self, model: DbtNode, context: ValidationContext):
    if not model.is_model():
        return []  # Skip early
```

### 4. Use Constants for Thresholds

```python
class MyValidator(BaseModelValidator):
    name = 'my_validator'

    MAX_COLUMNS = 50
    MAX_LINES = 200

    def validate(self, model, context):
        if len(columns) > self.MAX_COLUMNS:
            ..
```

### 5. Document Why Rules Exist

```python
class SecurityValidator(BaseModelValidator):
    """
    Ensure PII models follow security requirements.

    Background: GDPR compliance requires explicit PII tagging
    and retention policies for auditing purposes.
    """
    name = 'security_compliance'
```

### 6. Group Related Validators

```
validators/
  security/
    __init__.py
    pii_tagging.py
    retention_policy.py
  performance/
    __init__.py
    materialization.py
    column_count.py
  ownership/
    __init__.py
    owner_tags.py
    team_assignment.py
```

### 7. Version Control Validators

Commit validators to your dbt repo so team uses same rules.

## Troubleshooting

### Validator Not Discovered

- Check file doesn't start with `_`
- Ensure class inherits `BaseModelValidator` or `BaseProjectValidator`
- Verify `name` field is set
- Run with `--verbose` to see loaded validators

### Import Errors

```
ERROR: Failed to load validator: No module named 'dmp_af'
```

**Fix**: Install dmp-af in same environment:

```bash
pip install dmp-af
```

### Performance Issues

For project validators that iterate nodes:

```python
# Slow ❌
class SlowValidator(BaseProjectValidator):
    def validate(self, context):
        for node_id, node_dict in context.manifest['nodes'].items():
            node = DbtNode(**node_dict)  # Slow parse
            ..

# Fast ✅ - Use model validator instead
class FastValidator(BaseModelValidator):
    def validate(self, model, context):
        # Runner handles iteration and parsing
        ..
```

## Next Steps

- Read [Validation Framework](../features/validation.md) for complete API reference
- Check [Built-in Validators](https://github.com/yourusername/dmp-af/tree/main/dmp_af/validation/rules) for more examples
- Share validators with the community

## Related Documentation

- [Validation Framework](../features/validation.md)
- [CLI Reference](../reference/cli.md)
- [Testing Guide](../development/testing.md)
