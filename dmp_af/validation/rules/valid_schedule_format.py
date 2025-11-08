import re

from dmp_af.parser.dbt_node_model import DbtNode
from dmp_af.validation.context import ValidationContext
from dmp_af.validation.output.models import RuleViolation
from dmp_af.validation.rules.base import BaseModelValidator

# Common Airflow schedule presets
VALID_PRESETS = {
    '@once',
    '@hourly',
    '@daily',
    '@weekly',
    '@monthly',
    '@yearly',
    '@continuous',
    'None',
    'null',
}

# Simple cron pattern validation (basic check)
CRON_PATTERN = re.compile(
    r'^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*/[0-9]+)\s+'  # minute
    r'(\*|([0-9]|1[0-9]|2[0-3])|\*/[0-9]+)\s+'  # hour
    r'(\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*/[0-9]+)\s+'  # day
    r'(\*|([1-9]|1[0-2])|\*/[0-9]+)\s+'  # month
    r'(\*|[0-7]|\*/[0-9]+)$'  # day of week
)


class ValidScheduleFormatValidator(BaseModelValidator):
    """
    Validates that model schedules are valid cron expressions or presets.
    """

    name = 'valid_schedule_format'
    description = 'Model schedules are valid'

    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        if not model.is_model():
            return []

        if not hasattr(model.config, 'schedule') or model.config.schedule is None:
            return []

        schedule_name = (
            model.config.schedule.name if hasattr(model.config.schedule, 'name') else str(model.config.schedule)
        )

        # Check if it's a valid preset
        if schedule_name in VALID_PRESETS:
            return []

        # Check if it's a valid cron expression
        if CRON_PATTERN.match(schedule_name):
            return []

        return [
            RuleViolation(
                rule_name=self.name,
                message=f'Invalid schedule "{schedule_name}" - not a valid cron or preset',
                node_id=model.unique_id,
                severity=self.severity,
                suggestion=f'Use valid cron expression or preset: {", ".join(sorted(VALID_PRESETS))}',
            )
        ]
