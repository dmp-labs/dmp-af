from enum import Enum

import attrs


class Severity(str, Enum):
    """Severity level for validation violations."""

    ERROR = 'error'
    WARNING = 'warning'


@attrs.define(frozen=True)
class RuleViolation:
    rule_name: str = attrs.field(validator=attrs.validators.instance_of(str))
    message: str = attrs.field(validator=attrs.validators.instance_of(str))
    severity: Severity = attrs.field(validator=attrs.validators.instance_of(Severity))
    node_id: str | None = attrs.field(
        default=None,
        validator=attrs.validators.optional(attrs.validators.instance_of(str)),
    )
    suggestion: str | None = attrs.field(
        default=None,
        validator=attrs.validators.optional(attrs.validators.instance_of(str)),
    )
