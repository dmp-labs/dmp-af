from dmp_af.validation.output.models import RuleViolation, Severity


def format_violations(violations: list[RuleViolation]) -> str:
    """Format validation violations as plain text output."""
    if not violations:
        return '✓ All validations passed'

    output = []
    for v in violations:
        prefix = '[ERROR]' if v.severity == Severity.ERROR else '[WARNING]'
        output.append(f'{prefix} {v.rule_name}: {v.message}')
        if v.node_id:
            output.append(f'  Node: {v.node_id}')
        if v.suggestion:
            output.append(f'  Suggestion: {v.suggestion}')
        output.append('')

    errors = sum(1 for v in violations if v.severity == Severity.ERROR)
    warnings = sum(1 for v in violations if v.severity == Severity.WARNING)

    output.append('─' * 50)
    output.append(f'Summary: {errors} errors, {warnings} warnings')
    output.append('─' * 50)

    return '\n'.join(output)
