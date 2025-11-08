"""
Tests for validation framework using examples/dags manifest.
"""

import json
from pathlib import Path

import pytest
import yaml

from dmp_af.conf import Config, DbtDefaultTargetsConfig, DbtProjectConfig
from dmp_af.validation.context import ValidationContext
from dmp_af.validation.rules import get_builtin_validators
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


def test_builtin_validators_loaded():
    """Test that built-in validators are loaded correctly."""
    model_validators, project_validators = get_builtin_validators()

    assert len(model_validators) == 6
    assert len(project_validators) == 4

    model_names = {v.name for v in model_validators}
    assert 'parseable_dbt_nodes' in model_names
    assert 'conventional_model_name' in model_names
    assert 'airflow_task_name_length' in model_names
    assert 'source_freshness_config' in model_names
    assert 'snapshot_strategy_config' in model_names
    assert 'valid_schedule_format' in model_names

    project_names = {v.name for v in project_validators}
    assert 'unique_test_names' in project_names
    assert 'medium_test_parents' in project_names
    assert 'models_in_dags' in project_names
    assert 'kubernetes_profile_fields' in project_names


def test_validation_runner_executes(validation_context):
    """Test that ValidationRunner executes without crashing."""
    model_validators, project_validators = get_builtin_validators()
    runner = ValidationRunner(model_validators, project_validators)

    violations = runner.run(validation_context)

    # Should find some violations in the example project
    assert isinstance(violations, list)
    assert len(violations) > 0


def test_validation_context_lazy_graph(manifest, profiles, dbt_project, config):
    """Test that graph is lazy-loaded."""
    # Create fresh context
    fresh_context = ValidationContext(
        manifest=manifest,
        profiles=profiles,
        dbt_project=dbt_project,
        config=config,
    )

    # Graph should not be loaded initially
    assert fresh_context._graph is None

    # Access graph
    graph = fresh_context.graph

    # Graph should now be loaded
    assert fresh_context._graph is not None
    assert graph is fresh_context._graph


def test_parseable_dbt_nodes_validator(validation_context):
    """Test that parseable_dbt_nodes validator catches parsing errors."""
    from dmp_af.validation.rules.parseable_dbt_nodes import ParseableDbtNodesValidator

    validator = ParseableDbtNodesValidator()
    runner = ValidationRunner([validator], [])

    violations = runner.run(validation_context)

    # Node parser should not find violations (all nodes parse successfully)
    assert len(violations) == 0


def test_conventional_model_name_validator(validation_context):
    """Test that conventional_model_name validator catches naming issues."""
    from dmp_af.validation.rules.conventional_model_name import ConventionalModelNameValidator

    validator = ConventionalModelNameValidator()
    runner = ValidationRunner([validator], [])

    violations = runner.run(validation_context)

    # Example project has naming convention violations
    assert len(violations) > 0
    assert all(v.rule_name == 'conventional_model_name' for v in violations)
    assert all(v.severity == 'error' for v in violations)


def test_snapshot_strategy_config_validator(validation_context):
    """Test that snapshot_strategy_config validator catches snapshot config issues."""
    from dmp_af.validation.rules.snapshot_strategy_config import SnapshotStrategyConfigValidator

    validator = SnapshotStrategyConfigValidator()
    runner = ValidationRunner([validator], [])

    violations = runner.run(validation_context)

    # Example project has snapshot config violations
    assert len(violations) > 0
    assert all(v.rule_name == 'snapshot_strategy_config' for v in violations)
    assert all(v.severity == 'error' for v in violations)


def test_unique_test_names_validator(validation_context):
    """Test that unique_test_names validator checks for duplicate test names."""
    from dmp_af.validation.rules.unique_test_names import UniqueTestNamesValidator

    validator = UniqueTestNamesValidator()
    runner = ValidationRunner([], [validator])

    violations = runner.run(validation_context)

    # Example project should have unique test names
    assert len(violations) == 0


def test_models_in_dags_validator(validation_context):
    """Test that models_in_dags validator checks DAG generation."""
    from dmp_af.validation.rules.models_in_dags import ModelsInDagsValidator

    validator = ModelsInDagsValidator()
    runner = ValidationRunner([], [validator])

    violations = runner.run(validation_context)

    # Example project has model completeness issues
    assert len(violations) > 0
    assert all(v.rule_name == 'models_in_dags' for v in violations)


def test_exclude_rules(validation_context):
    """Test that rules can be excluded."""
    model_validators, project_validators = get_builtin_validators()

    # Exclude conventional_model_name
    filtered_model = [v for v in model_validators if v.name != 'conventional_model_name']
    filtered_project = [v for v in project_validators if v.name != 'models_in_dags']

    runner = ValidationRunner(filtered_model, filtered_project)
    violations = runner.run(validation_context)

    # Should not have any conventional_model_name or models_in_dags violations
    rule_names = {v.rule_name for v in violations}
    assert 'conventional_model_name' not in rule_names
    assert 'models_in_dags' not in rule_names


def test_filter_specific_rules(validation_context):
    """Test that only specific rules can be run."""
    model_validators, project_validators = get_builtin_validators()

    # Only run parseable_dbt_nodes
    filtered_model = [v for v in model_validators if v.name == 'parseable_dbt_nodes']
    filtered_project = []

    runner = ValidationRunner(filtered_model, filtered_project)
    violations = runner.run(validation_context)

    # Should have no violations (parseable_dbt_nodes doesn't catch anything)
    assert len(violations) == 0
