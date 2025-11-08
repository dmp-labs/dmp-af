from dmp_af.parser.dbt_node_model import DbtNode
from dmp_af.validation.context import ValidationContext
from dmp_af.validation.output.models import RuleViolation
from dmp_af.validation.rules.base import BaseModelValidator


class ConventionalModelNameValidator(BaseModelValidator):
    """
    Validates that dbt node names match their path structure.
    Expected pattern: {fqn[1]}.{fqn[2]}.{name.split(".")[-1]}
    """

    name = 'conventional_model_name'
    description = 'Node name matches path structure'

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        if not model.is_model():
            return []

        real_node_name = model.fqn[-1]
        expected_node_name = f'{model.fqn[1]}.{model.fqn[2]}.{model.name.split(".")[-1]}'

        if real_node_name != expected_node_name:
            return [
                RuleViolation(
                    rule_name=self.name,
                    message=f'Node name mismatch: expected "{expected_node_name}", got "{real_node_name}"',
                    node_id=model.unique_id,
                    severity=self.severity,
                    suggestion='Ensure model file path matches naming convention',
                )
            ]

        return []
