from dmp_af.parser.dbt_node_model import DbtNode
from dmp_af.validation.context import ValidationContext
from dmp_af.validation.output.models import RuleViolation
from dmp_af.validation.rules.base import BaseModelValidator


class SnapshotStrategyConfigValidator(BaseModelValidator):
    """
    Validates dbt snapshots have required configuration fields.
    """

    name = 'snapshot_strategy_config'
    description = 'dbt snapshots have required configuration'

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        if not model.is_snapshot():
            return []

        violations = []
        required_fields = ['strategy', 'unique_key', 'target_schema']

        for field in required_fields:
            if not hasattr(model.config, field) or getattr(model.config, field, None) is None:
                violations.append(
                    RuleViolation(
                        rule_name=self.name,
                        message=f'Snapshot missing required field: {field}',
                        node_id=model.unique_id,
                        severity=self.severity,
                        suggestion=f'Add {field} to snapshot configuration',
                    )
                )

        return violations
