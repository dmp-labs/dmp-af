from collections import defaultdict

from dmp_af.dags import dbt_main_dags
from dmp_af.parser.dbt_node_model import DbtNode
from dmp_af.validation.context import ValidationContext
from dmp_af.validation.output.models import RuleViolation
from dmp_af.validation.rules.base import BaseProjectValidator


def _model_safe_name(node: DbtNode) -> str:
    return node.fqn[-1].replace('.', '__')


def _model_schedule_safe_name(schedule_name: str) -> str:
    return schedule_name.replace('@', '')


class ModelsInDagsValidator(BaseProjectValidator):
    """
    Validates that all dbt models from manifest appear in generated Airflow DAGs.
    """

    name = 'models_in_dags'
    description = 'All dbt models appear in generated DAGs'
    needs_graph = True

    def validate(self, context: ValidationContext) -> list[RuleViolation]:
        violations = []

        dags = dbt_main_dags(context.graph)

        raw_dbt_nodes_by_domain_schedule = defaultdict(lambda: defaultdict(set))
        for raw_node in context.manifest['nodes'].values():
            try:
                node = DbtNode(**raw_node)
                if not node.is_model():
                    continue

                raw_dbt_nodes_by_domain_schedule[node.domain][_model_schedule_safe_name(node.config.schedule.name)].add(
                    _model_safe_name(node)
                )
            except (ValueError, TypeError, KeyError, AttributeError):
                continue

        for dag_name, dag in dags.items():
            if (
                'dbt' not in dag.tags
                or 'backfill' in dag.tags
                or 'frontier' not in dag.tags
                or 'dbt_large_tests' in dag.tags
            ):
                continue

            domain_name, schedule, *_ = dag_name.split('__')
            task_ids = [
                task.task_id.split('.')[-1]
                for task in dag.tasks
                if task.operator_name not in ('DbtTest', 'EmptyOperator', 'DbtBranchOperator')
            ]
            task_ids_by_domain = [
                task_id
                for task_id in task_ids
                if task_id.startswith(domain_name) and not task_id.endswith('_increment')
            ]

            expected_models = raw_dbt_nodes_by_domain_schedule[domain_name][schedule]
            actual_models = set(task_ids_by_domain)

            missing_models = expected_models - actual_models
            extra_models = actual_models - expected_models

            if missing_models:
                violations.append(
                    RuleViolation(
                        rule_name=self.name,
                        message=f'Models missing from DAG {dag_name}: {", ".join(sorted(missing_models)[:5])}',
                        severity=self.severity,
                        suggestion='Check DAG generation logic',
                    )
                )

            if extra_models:
                extra_list = ', '.join(sorted(extra_models)[:5])
                violations.append(
                    RuleViolation(
                        rule_name=self.name,
                        message=f'Extra models in DAG {dag_name} not in manifest: {extra_list}',
                        severity=self.severity,
                        suggestion='Regenerate manifest or check DAG generation',
                    )
                )

        return violations
