from abc import ABC, abstractmethod

from dmp_af.parser.dbt_node_model import DbtNode
from dmp_af.validation.context import ValidationContext
from dmp_af.validation.output.models import RuleViolation, Severity


class BaseModelValidator(ABC):
    """
    Base class for validators that run per-model.
    Subclass this to create custom validators that check individual dbt nodes.

    Example:
        class StagingNamingRule(BaseModelValidator):
            name = "staging_naming"
            description = "Staging models must start with stg_"
            severity = Severity.ERROR

            def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
                if not model.name.startswith("stg_"):
                    return [RuleViolation(
                        rule_name=self.name,
                        message="Staging model must start with stg_",
                        node_id=model.unique_id,
                        severity=self.severity,
                    )]
                return []
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Validator name (required). Override with class attribute: name = 'my_validator'"""
        raise NotImplementedError(f'{self.__class__.__name__} must define "name" attribute')

    @property
    def description(self) -> str:
        """Validator description (optional). Override with class attribute: description = 'My description'"""
        return ''

    @property
    def severity(self) -> Severity:
        """Severity level (optional). Override with class attribute: severity = Severity.ERROR"""
        return Severity.ERROR

    @abstractmethod
    def validate(self, model: DbtNode, context: ValidationContext) -> list[RuleViolation]:
        """
        Validate a single dbt model node.

        :param model: The dbt node to validate
        :param context: Validation context with access to manifest, profiles, config, and graph
        :return: List of violations found (empty list if valid)
        """
        pass


class BaseProjectValidator(ABC):
    """
    Base class for validators that run once on the entire project.
    Subclass this to create custom validators that check project-wide constraints.

    Example:
        class CrossDomainDepsRule(BaseProjectValidator):
            name = "cross_domain_deps"
            description = "Check cross-domain dependencies"
            severity = Severity.WARNING
            needs_graph = True

            def validate(self, context: ValidationContext) -> list[RuleViolation]:
                violations = []
                for node_id in context.manifest['nodes']:
                    # Check logic here
                    pass
                return violations
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Validator name (required). Override with class attribute: name = 'my_validator'"""
        raise NotImplementedError(f'{self.__class__.__name__} must define "name" attribute')

    @property
    def description(self) -> str:
        """Validator description (optional). Override with class attribute: description = 'My description'"""
        return ''

    @property
    def severity(self) -> Severity:
        """Severity level (optional). Override with class attribute: severity = Severity.ERROR"""
        return Severity.ERROR

    @property
    def needs_graph(self) -> bool:
        """Whether validator needs graph (optional). Override with class attribute: needs_graph = True"""
        return False

    @abstractmethod
    def validate(self, context: ValidationContext) -> list[RuleViolation]:
        """
        Validate the entire dbt project.

        :param context: Validation context with access to manifest, profiles, config, and graph
        :return: List of violations found (empty list if valid)
        """
        pass
