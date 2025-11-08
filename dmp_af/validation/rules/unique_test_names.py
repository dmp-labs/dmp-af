from dmp_af.parser.dbt_node_model import DbtNode
from dmp_af.validation.context import ValidationContext
from dmp_af.validation.output.models import RuleViolation
from dmp_af.validation.rules.base import BaseProjectValidator


class UniqueTestNamesValidator(BaseProjectValidator):
    """
    Validates that all dbt validation names are unique across the project.
    """

    name = 'unique_test_names'
    description = 'All dbt validations have unique names'

    def validate(self, context: ValidationContext) -> list[RuleViolation]:
        violations = []
        unique_test_names = set()
        duplicate_tests = {}

        for node_dict in context.manifest.get('nodes', {}).values():
            try:
                node = DbtNode(**node_dict)
                if node.is_test():
                    test_name = node.name

                    if test_name in unique_test_names:
                        if test_name not in duplicate_tests:
                            duplicate_tests[test_name] = []
                        duplicate_tests[test_name].append(node.unique_id)
                    else:
                        unique_test_names.add(test_name)
            except (ValueError, TypeError, KeyError):
                continue

        for test_name, node_ids in duplicate_tests.items():
            violations.append(
                RuleViolation(
                    rule_name=self.name,
                    message=f'Duplicate validation name "{test_name}" found in {len(node_ids) + 1} validations',
                    severity=self.severity,
                    suggestion=f'Rename validations to make them unique. Affected nodes: {", ".join(node_ids[:3])}',
                )
            )

        return violations
