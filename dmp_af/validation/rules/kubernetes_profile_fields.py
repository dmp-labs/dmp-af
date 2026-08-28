from dmp_af.parser.dbt_profiles import Profile
from dmp_af.validation.context import ValidationContext
from dmp_af.validation.output.models import RuleViolation
from dmp_af.validation.rules.base import BaseProjectValidator


class KubernetesProfileFieldsValidator(BaseProjectValidator):
    """
    Validates that Kubernetes targets in profiles have required fields.
    Required fields: node_pool_selector_name, node_pool, image_name,
                     pod_cpu_guarantee, pod_memory_guarantee, tolerations
    """

    name = 'kubernetes_profile_fields'
    description = 'Kubernetes targets have required configuration'

    def validate(self, context: ValidationContext) -> list[RuleViolation]:
        violations = []

        required_fields = [
            'node_pool_selector_name',
            'node_pool',
            'image_name',
            'pod_cpu_guarantee',
            'pod_memory_guarantee',
            'tolerations',
        ]

        for profile_name, profile_dict in context.profiles.items():
            if profile_name == 'config':
                continue

            try:
                profile = Profile(**profile_dict)
                for target_name, target in profile.outputs.items():
                    if target.target_type == 'kubernetes':
                        for field in required_fields:
                            if getattr(target, field, None) is None:
                                violations.append(
                                    RuleViolation(
                                        rule_name=self.name,
                                        message=f'Kubernetes target missing required field: {field}',
                                        node_id=f'profile.{profile_name}.{target_name}',
                                        severity=self.severity,
                                        suggestion=f'Add {field} to target {target_name} in profile {profile_name}',
                                    )
                                )
            except Exception as e:
                violations.append(
                    RuleViolation(
                        rule_name=self.name,
                        message=f'Failed to parse profile {profile_name}: {e}',
                        severity=self.severity,
                    )
                )

        return violations
