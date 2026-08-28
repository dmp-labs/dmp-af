from dmp_af.parser.dbt_node_model import DbtNode
from dmp_af.validation.context import ValidationContext
from dmp_af.validation.output.models import RuleViolation, Severity
from dmp_af.validation.rules.base import BaseModelValidator


class SourceFreshnessConfigValidator(BaseModelValidator):
    """
    Validates dbt sources have freshness configuration.
    """

    name = 'source_freshness_config'
    description = 'dbt sources have freshness configuration'
    severity = Severity.WARNING

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        # Check resource_type since DbtNode doesn't have is_source() method
        if model.resource_type != 'source':
            return []

        violations = []

        # Check freshness config
        if not hasattr(model.config, 'freshness') or model.config.freshness is None:
            violations.append(
                RuleViolation(
                    rule_name=self.name,
                    message='Source missing freshness configuration',
                    node_id=model.unique_id,
                    severity=self.severity,
                    suggestion='Add freshness config to source definition',
                )
            )

        return violations
