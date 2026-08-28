from dmp_af.validation.context import ValidationContext
from dmp_af.validation.output.models import RuleViolation
from dmp_af.validation.rules.base import BaseProjectValidator


class MediumTestParentsValidator(BaseProjectValidator):
    """
    Validates that all medium validations have parent nodes.
    """

    name = 'medium_test_parents'
    description = 'Medium validations have parent nodes'
    needs_graph = True

    def validate(self, context: ValidationContext) -> list[RuleViolation]:
        violations = []

        for node in context.graph.dbt_nodes:
            if node.is_medium_test():
                try:
                    context.graph._find_parent_node_for_test(node)
                except Exception as e:
                    violations.append(
                        RuleViolation(
                            rule_name=self.name,
                            message=f'Medium validation has no parent node: {e}',
                            node_id=node.unique_id,
                            severity=self.severity,
                            suggestion='Ensure medium validation is attached to a valid model',
                        )
                    )

        return violations
