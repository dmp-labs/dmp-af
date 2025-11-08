from dmp_af.parser.dbt_node_model import DbtNode
from dmp_af.validation.context import ValidationContext
from dmp_af.validation.output.models import RuleViolation
from dmp_af.validation.rules.base import BaseModelValidator


class ParseableDbtNodesValidator(BaseModelValidator):
    """
    Validates that DbtNode can parse all manifest nodes without crashing.
    This is a smoke test - actual parsing happens in the runner.
    """

    name = 'parseable_dbt_nodes'
    description = 'DbtNode parsing smoke test'

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        # If we got here, parsing succeeded
        return []
