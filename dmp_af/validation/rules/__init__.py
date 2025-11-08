from dmp_af.validation.rules.airflow_task_name_length import AirflowTaskNameLengthValidator
from dmp_af.validation.rules.conventional_model_name import ConventionalModelNameValidator
from dmp_af.validation.rules.kubernetes_profile_fields import KubernetesProfileFieldsValidator
from dmp_af.validation.rules.medium_test_parents import MediumTestParentsValidator
from dmp_af.validation.rules.models_in_dags import ModelsInDagsValidator
from dmp_af.validation.rules.parseable_dbt_nodes import ParseableDbtNodesValidator
from dmp_af.validation.rules.snapshot_strategy_config import SnapshotStrategyConfigValidator
from dmp_af.validation.rules.source_freshness_config import SourceFreshnessConfigValidator
from dmp_af.validation.rules.unique_test_names import UniqueTestNamesValidator
from dmp_af.validation.rules.valid_schedule_format import ValidScheduleFormatValidator


def get_builtin_validators():
    """Get all built-in validators."""
    model_validators = [
        ParseableDbtNodesValidator(),
        ConventionalModelNameValidator(),
        AirflowTaskNameLengthValidator(),
        SourceFreshnessConfigValidator(),
        SnapshotStrategyConfigValidator(),
        ValidScheduleFormatValidator(),
    ]

    project_validators = [
        UniqueTestNamesValidator(),
        MediumTestParentsValidator(),
        ModelsInDagsValidator(),
        KubernetesProfileFieldsValidator(),
    ]

    return model_validators, project_validators
