"""
Tests for custom rule loading and discovery.
"""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from dmp_af.conf import Config, DbtDefaultTargetsConfig, DbtProjectConfig
from dmp_af.validation.context import ValidationContext
from dmp_af.validation.loader import load_custom_rules
from dmp_af.validation.output.models import Severity
from dmp_af.validation.runner import ValidationRunner


@pytest.fixture(scope='module')
def examples_dir():
    """Path to examples directory."""
    return Path(__file__).parent.parent.parent / 'examples' / 'dags'


@pytest.fixture(scope='module')
def manifest(examples_dir):
    """Load manifest from examples."""
    manifest_path = examples_dir / 'target' / 'manifest.json'
    return json.loads(manifest_path.read_text())


@pytest.fixture(scope='module')
def profiles(examples_dir):
    """Load profiles from examples."""
    profiles_path = examples_dir / 'profiles.yml'
    return yaml.safe_load(profiles_path.read_text())


@pytest.fixture(scope='module')
def dbt_project(examples_dir):
    """Load dbt_project from examples."""
    dbt_project_path = examples_dir / 'dbt_project.yml'
    return yaml.safe_load(dbt_project_path.read_text())


@pytest.fixture(scope='module')
def config(examples_dir, dbt_project):
    """Create Config for validation."""
    return Config(
        dbt_project=DbtProjectConfig(
            dbt_project_name=dbt_project['name'],
            dbt_models_path=examples_dir / 'models',
            dbt_project_path=examples_dir,
            dbt_profiles_path=examples_dir,
            dbt_target_path=examples_dir / 'target',
            dbt_log_path=examples_dir / 'target' / 'logs',
            dbt_schema='schema',
        ),
        dbt_default_targets=DbtDefaultTargetsConfig(default_target='dev'),
    )


@pytest.fixture(scope='module')
def validation_context(manifest, profiles, dbt_project, config):
    """Create ValidationContext."""
    return ValidationContext(
        manifest=manifest,
        profiles=profiles,
        dbt_project=dbt_project,
        config=config,
    )


def test_load_custom_model_validator(validation_context):
    """Test loading custom model validator from file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_rules_dir = Path(tmpdir)

        # Create custom model validator
        custom_rule_file = custom_rules_dir / 'my_custom_rule.py'
        custom_rule_file.write_text("""
from dmp_af.validation import BaseModelValidator, RuleViolation, Severity, ValidationContext
from dmp_af.parser.dbt_node_model import DbtNode

class MyCustomValidator(BaseModelValidator):
    name = "my_custom"
    description = "Custom validation rule"
    severity = Severity.WARNING

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        # Always return a violation for testing
        if model.is_model():
            return [RuleViolation(
                rule_name=self.name,
                message="Custom validation triggered",
                node_id=model.unique_id,
                severity=self.severity,
            )]
        return []
""")

        # Load custom rules
        model_validators, project_validators = load_custom_rules(custom_rules_dir)

        # Should have loaded one model validator
        assert len(model_validators) == 1
        assert len(project_validators) == 0
        assert model_validators[0].name == 'my_custom'
        assert model_validators[0].severity == Severity.WARNING

        # Run validator
        runner = ValidationRunner(model_validators, [])
        violations = runner.run(validation_context)

        # Should find violations
        assert len(violations) > 0
        assert all(v.rule_name == 'my_custom' for v in violations)
        assert all(v.severity == Severity.WARNING for v in violations)


def test_load_custom_project_validator(validation_context):
    """Test loading custom project validator from file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_rules_dir = Path(tmpdir)

        # Create custom project validator
        custom_rule_file = custom_rules_dir / 'project_check.py'
        custom_rule_file.write_text("""
from dmp_af.validation import BaseProjectValidator, RuleViolation, Severity, ValidationContext

class ProjectLevelCheck(BaseProjectValidator):
    name = "project_level"
    description = "Project-wide validation"

    def validate(self, context: ValidationContext) -> list[RuleViolation]:
        # Check manifest has nodes
        if len(context.manifest.get('nodes', {})) > 0:
            return [RuleViolation(
                rule_name=self.name,
                message="Project has nodes",
                severity=self.severity,
            )]
        return []
""")

        # Load custom rules
        model_validators, project_validators = load_custom_rules(custom_rules_dir)

        # Should have loaded one project validator
        assert len(model_validators) == 0
        assert len(project_validators) == 1
        assert project_validators[0].name == 'project_level'
        assert project_validators[0].needs_graph is False

        # Run validator
        runner = ValidationRunner([], project_validators)
        violations = runner.run(validation_context)

        # Should find exactly one violation
        assert len(violations) == 1
        assert violations[0].rule_name == 'project_level'
        assert violations[0].severity == Severity.ERROR


def test_load_custom_validator_with_graph_access(validation_context):
    """Test loading custom validator that needs graph."""
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_rules_dir = Path(tmpdir)

        # Create custom validator that needs graph
        custom_rule_file = custom_rules_dir / 'graph_check.py'
        custom_rule_file.write_text("""
from dmp_af.validation import BaseProjectValidator, RuleViolation, Severity, ValidationContext

class GraphAccessValidator(BaseProjectValidator):
    name = "graph_access"
    description = "Validator that accesses graph"
    severity = Severity.WARNING
    needs_graph = True

    def validate(self, context: ValidationContext) -> list[RuleViolation]:
        # Access graph (should trigger lazy load)
        graph = context.graph
        if len(graph.dbt_nodes) > 0:
            return [RuleViolation(
                rule_name=self.name,
                message=f"Graph has {len(graph.dbt_nodes)} nodes",
                severity=self.severity,
            )]
        return []
""")

        # Load custom rules
        model_validators, project_validators = load_custom_rules(custom_rules_dir)

        # Should have loaded validator with needs_graph=True
        assert len(project_validators) == 1
        assert project_validators[0].needs_graph is True

        # Run validator (should load graph)
        runner = ValidationRunner([], project_validators)
        violations = runner.run(validation_context)

        # Should find violation
        assert len(violations) == 1
        assert violations[0].rule_name == 'graph_access'


def test_load_multiple_custom_validators(validation_context):
    """Test loading multiple custom validators from same folder."""
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_rules_dir = Path(tmpdir)

        # Create multiple custom validators
        (custom_rules_dir / 'validator1.py').write_text("""
from dmp_af.validation import BaseModelValidator, RuleViolation, ValidationContext
from dmp_af.parser.dbt_node_model import DbtNode

class Validator1(BaseModelValidator):
    name = "validator1"

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        return []
""")

        (custom_rules_dir / 'validator2.py').write_text("""
from dmp_af.validation import BaseModelValidator, RuleViolation, Severity, ValidationContext
from dmp_af.parser.dbt_node_model import DbtNode

class Validator2(BaseModelValidator):
    name = "validator2"
    severity = Severity.WARNING

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        return []
""")

        (custom_rules_dir / 'project_validator.py').write_text("""
from dmp_af.validation import BaseProjectValidator, RuleViolation, ValidationContext

class ProjectValidator(BaseProjectValidator):
    name = "project_validator"

    def validate(self, context: ValidationContext) -> list[RuleViolation]:
        return []
""")

        # Load custom rules
        model_validators, project_validators = load_custom_rules(custom_rules_dir)

        # Should have loaded all validators
        assert len(model_validators) == 2
        assert len(project_validators) == 1

        model_names = {v.name for v in model_validators}
        assert 'validator1' in model_names
        assert 'validator2' in model_names

        project_names = {v.name for v in project_validators}
        assert 'project_validator' in project_names


def test_skip_files_starting_with_underscore():
    """Test that files starting with _ are skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_rules_dir = Path(tmpdir)

        # Create file starting with _
        (custom_rules_dir / '_helpers.py').write_text("""
from dmp_af.validation import BaseModelValidator, RuleViolation, ValidationContext
from dmp_af.parser.dbt_node_model import DbtNode

class ShouldBeSkipped(BaseModelValidator):
    name = "skipped"

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        return []
""")

        # Create normal file
        (custom_rules_dir / 'normal.py').write_text("""
from dmp_af.validation import BaseModelValidator, RuleViolation, ValidationContext
from dmp_af.parser.dbt_node_model import DbtNode

class NormalValidator(BaseModelValidator):
    name = "normal"

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        return []
""")

        # Load custom rules
        model_validators, project_validators = load_custom_rules(custom_rules_dir)

        # Should only load normal.py
        assert len(model_validators) == 1
        assert model_validators[0].name == 'normal'


def test_handles_broken_custom_validator_gracefully():
    """Test that broken custom validators are logged but don't crash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_rules_dir = Path(tmpdir)

        # Create broken validator (syntax error)
        (custom_rules_dir / 'broken.py').write_text("""
from dmp_af.validation import BaseModelValidator

class BrokenValidator(BaseModelValidator
    # Missing closing parenthesis - syntax error
""")

        # Create working validator
        (custom_rules_dir / 'working.py').write_text("""
from dmp_af.validation import BaseModelValidator, RuleViolation, ValidationContext
from dmp_af.parser.dbt_node_model import DbtNode

class WorkingValidator(BaseModelValidator):
    name = "working"

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        return []
""")

        # Load custom rules (should not crash)
        model_validators, project_validators = load_custom_rules(custom_rules_dir)

        # Should only load working validator
        assert len(model_validators) == 1
        assert model_validators[0].name == 'working'


def test_handles_validator_instantiation_error():
    """Test that validators that fail to instantiate are skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_rules_dir = Path(tmpdir)

        # Create validator that fails to instantiate
        (custom_rules_dir / 'bad_init.py').write_text("""
from dmp_af.validation import BaseModelValidator, RuleViolation, ValidationContext
from dmp_af.parser.dbt_node_model import DbtNode

class BadInitValidator(BaseModelValidator):
    name = "bad_init"

    def __init__(self):
        raise ValueError("Cannot instantiate!")

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        return []
""")

        # Load custom rules (should not crash)
        model_validators, project_validators = load_custom_rules(custom_rules_dir)

        # Should not load any validators
        assert len(model_validators) == 0
        assert len(project_validators) == 0


def test_nonexistent_folder_returns_empty():
    """Test that nonexistent folder returns empty lists."""
    nonexistent = Path('/tmp/definitely_does_not_exist_12345')

    model_validators, project_validators = load_custom_rules(nonexistent)

    assert len(model_validators) == 0
    assert len(project_validators) == 0


def test_file_instead_of_folder_returns_empty():
    """Test that passing a file instead of folder returns empty lists."""
    with tempfile.NamedTemporaryFile(suffix='.py') as tmp:
        file_path = Path(tmp.name)

        model_validators, project_validators = load_custom_rules(file_path)

        assert len(model_validators) == 0
        assert len(project_validators) == 0


def test_custom_validator_can_access_model_attributes(validation_context):
    """Test that custom validators can access model attributes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_rules_dir = Path(tmpdir)

        # Create validator that checks model attributes
        custom_rule_file = custom_rules_dir / 'attribute_check.py'
        custom_rule_file.write_text("""
from dmp_af.validation import BaseModelValidator, RuleViolation, Severity, ValidationContext
from dmp_af.parser.dbt_node_model import DbtNode

class AttributeCheckValidator(BaseModelValidator):
    name = "attribute_check"
    severity = Severity.WARNING

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        # Access various model attributes
        if model.is_model() and hasattr(model, 'fqn') and len(model.fqn) > 0:
            return [RuleViolation(
                rule_name=self.name,
                message=f"Model FQN: {'.'.join(model.fqn)}",
                node_id=model.unique_id,
                severity=self.severity,
            )]
        return []
""")

        # Load and run
        model_validators, project_validators = load_custom_rules(custom_rules_dir)
        runner = ValidationRunner(model_validators, [])
        violations = runner.run(validation_context)

        # Should find violations with FQN info
        assert len(violations) > 0
        assert all('Model FQN:' in v.message for v in violations)
