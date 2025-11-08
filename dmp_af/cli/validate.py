import json
import logging
from pathlib import Path
from typing import Optional

import typer
import yaml

from dmp_af.cli import app
from dmp_af.conf import Config, DbtDefaultTargetsConfig, DbtProjectConfig
from dmp_af.validation.context import ValidationContext
from dmp_af.validation.loader import load_custom_rules
from dmp_af.validation.output.formatter import format_violations
from dmp_af.validation.output.models import Severity
from dmp_af.validation.rules import get_builtin_validators
from dmp_af.validation.runner import ValidationRunner

logger = logging.getLogger(__name__)


@app.command(name='validate')
def validate(
    manifest_path: str = typer.Option(..., help='Path to manifest.json or directory containing it'),
    profiles_path: str = typer.Option(..., help='Path to profiles.yml or directory containing it'),
    dbt_project_path: str = typer.Option(..., help='Path to dbt_project.yml or directory containing it'),
    models_path: str = typer.Option(..., help='Path to models directory'),
    target: str = typer.Option('dev', help='Default dbt target'),
    custom_rules_path: Optional[str] = typer.Option(
        None, help='Path to custom validators folder (WARNING: executes Python code from this folder)'
    ),
    rules: Optional[str] = typer.Option(None, help='Comma-separated rule names to run (runs all if not specified)'),
    exclude_rules: Optional[str] = typer.Option(None, help='Comma-separated rule names to exclude'),
    warnings_as_errors: bool = typer.Option(False, help='Treat warnings as errors'),
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Enable verbose logging'),
):
    """
    Validate dbt project manifest and configuration.

    This command runs built-in and custom validation rules against your dbt project.
    """
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(levelname)s: %(message)s',
    )

    try:
        # Resolve paths
        manifest_file = Path(manifest_path)
        if manifest_file.is_dir():
            manifest_file = manifest_file / 'manifest.json'

        profiles_file = Path(profiles_path)
        if profiles_file.is_dir():
            profiles_file = profiles_file / 'profiles.yml'

        dbt_project_file = Path(dbt_project_path)
        if dbt_project_file.is_dir():
            dbt_project_file = dbt_project_file / 'dbt_project.yml'

        models_dir = Path(models_path)

        # Load artifacts
        logger.info(f'Loading manifest from {manifest_file}')
        with manifest_file.open('r') as f:
            manifest = json.load(f)

        logger.info(f'Loading profiles from {profiles_file}')
        with profiles_file.open('r') as f:
            profiles = yaml.safe_load(f)

        logger.info(f'Loading dbt_project from {dbt_project_file}')
        with dbt_project_file.open('r') as f:
            dbt_project = yaml.safe_load(f)

        # Build Config
        config = Config(
            dbt_project=DbtProjectConfig(
                dbt_project_name=dbt_project['name'],
                dbt_models_path=models_dir,
                dbt_project_path=dbt_project_file.parent,
                dbt_profiles_path=profiles_file.parent,
                dbt_target_path=manifest_file.parent,
                dbt_log_path=manifest_file.parent / 'logs',
                dbt_schema='schema',  # Default schema
            ),
            dbt_default_targets=DbtDefaultTargetsConfig(default_target=target),
        )

        # Build ValidationContext
        context = ValidationContext(
            manifest=manifest,
            profiles=profiles,
            dbt_project=dbt_project,
            config=config,
        )

        # Load validators
        logger.info('Loading built-in validators')
        model_validators, project_validators = get_builtin_validators()

        if custom_rules_path:
            logger.info(f'Loading custom validators from {custom_rules_path}')
            custom_model, custom_project = load_custom_rules(Path(custom_rules_path))
            model_validators.extend(custom_model)
            project_validators.extend(custom_project)

        # Filter validators
        if rules:
            filter_names = set(rules.split(','))
            logger.info(f'Running only rules: {filter_names}')
            model_validators = [v for v in model_validators if v.name in filter_names]
            project_validators = [v for v in project_validators if v.name in filter_names]

        if exclude_rules:
            exclude_names = set(exclude_rules.split(','))
            logger.info(f'Excluding rules: {exclude_names}')
            model_validators = [v for v in model_validators if v.name not in exclude_names]
            project_validators = [v for v in project_validators if v.name not in exclude_names]

        logger.info(
            f'Running {len(model_validators)} model validators and {len(project_validators)} project validators'
        )

        # Run validation
        runner = ValidationRunner(model_validators, project_validators)
        violations = runner.run(context)

        # Format and print output
        output = format_violations(violations)
        print(output)

        # Exit code
        errors = [v for v in violations if v.severity == Severity.ERROR]
        warnings = [v for v in violations if v.severity == Severity.WARNING]

        if errors or (warnings and warnings_as_errors):
            raise typer.Exit(1)

    except FileNotFoundError as e:
        logger.error(f'File not found: {e}')
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f'Validation failed: {e}', exc_info=verbose)
        raise typer.Exit(1)
