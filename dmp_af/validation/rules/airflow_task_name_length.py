from dmp_af.parser.dbt_node_model import DbtNode
from dmp_af.validation.context import ValidationContext
from dmp_af.validation.output.models import RuleViolation
from dmp_af.validation.rules.base import BaseModelValidator

# Airflow task_id max length is 250 chars
MAX_TASK_ID_LENGTH = 250
# Model dependencies reserve 5 chars for suffix pattern __{dep_number} where 0 <= dep_number <= 999
MAX_MODEL_DEP_WAIT_TASK_LENGTH = 245


class AirflowTaskNameLengthValidator(BaseModelValidator):
    """
    Validates that Airflow wait task names are within length limits.
    - Model dependencies: ≤245 chars (5 reserved for suffix)
    - Test dependencies: ≤250 chars
    """

    name = 'airflow_task_name_length'
    description = 'Airflow task names within length limits'

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        violations = []

        # Get raw node dict to access depends_on
        node_dict = context.manifest['nodes'].get(model.unique_id)
        if not node_dict:
            return violations

        if model.is_model():
            for dep in node_dict.get('depends_on', {}).get('nodes', []):
                if dep.startswith('model'):
                    dep_node_dict = context.manifest['nodes'].get(dep)
                    if not dep_node_dict:
                        continue

                    dep_name = dep_node_dict['name']
                    dep_safe_name = dep_name.replace('.', '__')
                    dep_domain_name = dep_name.split('.')[0]
                    wait_name = f'{dep_domain_name}__scheduletag__dependencies__group.wait__{dep_safe_name}'

                    if len(wait_name) > MAX_MODEL_DEP_WAIT_TASK_LENGTH:
                        msg = f'Wait task name too long ({len(wait_name)} chars, max {MAX_MODEL_DEP_WAIT_TASK_LENGTH})'
                        violations.append(
                            RuleViolation(
                                rule_name=self.name,
                                message=msg,
                                node_id=model.unique_id,
                                severity=self.severity,
                                suggestion=f'Shorten model name or domain structure. Wait name: {wait_name}',
                            )
                        )

        elif model.is_test():
            for dep in node_dict.get('depends_on', {}).get('nodes', []):
                if dep.startswith('model'):
                    model_name_safe_name = '.'.join(dep.split('.')[2:]).replace('.', '__')
                    wait_name = f'{model_name_safe_name}__group.{model.name}'

                    if len(wait_name) > MAX_TASK_ID_LENGTH:
                        msg = f'Test wait task name too long ({len(wait_name)} chars, max {MAX_TASK_ID_LENGTH})'
                        violations.append(
                            RuleViolation(
                                rule_name=self.name,
                                message=msg,
                                node_id=model.unique_id,
                                severity=self.severity,
                                suggestion=f'Shorten validation or model name. Wait name: {wait_name}',
                            )
                        )

        return violations
