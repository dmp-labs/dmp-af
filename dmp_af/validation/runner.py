import logging

from dmp_af.parser.dbt_node_model import DbtNode
from dmp_af.validation.context import ValidationContext
from dmp_af.validation.output.models import RuleViolation
from dmp_af.validation.rules.base import BaseModelValidator, BaseProjectValidator

logger = logging.getLogger(__name__)


class ValidationRunner:
    """
    Orchestrates execution of model and project validators.
    """

    def __init__(
        self,
        model_validators: list[BaseModelValidator],
        project_validators: list[BaseProjectValidator],
    ):
        self.model_validators = model_validators
        self.project_validators = project_validators

    def run(self, context: ValidationContext) -> list[RuleViolation]:
        """
        Run all validators and collect violations.

        :param context: Validation context with manifest, profiles, config, etc
        :return: List of all violations found
        """
        violations = []

        # Run model validators per-node
        logger.info(f'Running {len(self.model_validators)} model validators')
        for node_id, node_dict in context.manifest.get('nodes', {}).items():
            resource_type = node_dict.get('resource_type')
            if resource_type not in ['model', 'snapshot', 'seed']:
                continue

            try:
                node = DbtNode(**node_dict)
                for validator in self.model_validators:
                    try:
                        validator_violations = validator.validate(node, context)
                        violations.extend(validator_violations)
                    except (ValueError, TypeError, KeyError, AttributeError) as e:
                        logger.error(f'Validator {validator.name} failed on node {node_id}: {e}')
                        continue
            except (ValueError, TypeError, KeyError) as e:
                logger.debug(f'Skipping unparseable node {node_id}: {e}')
                continue

        # Load graph only if any validator needs it
        graph_validators = [v for v in self.project_validators if v.needs_graph]
        if graph_validators:
            logger.info(f'{len(graph_validators)} validators need graph, loading...')
            _ = context.graph  # Trigger lazy load

        # Run project validators once
        logger.info(f'Running {len(self.project_validators)} project validators')
        for validator in self.project_validators:
            try:
                validator_violations = validator.validate(context)
                violations.extend(validator_violations)
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.error(f'Validator {validator.name} failed: {e}')
                continue

        return violations
