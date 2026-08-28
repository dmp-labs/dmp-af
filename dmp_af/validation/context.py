from typing import TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from dmp_af.builder.dmp_af_builder import DmpAfGraph
    from dmp_af.conf import Config


@attrs.define
class ValidationContext:
    """
    Context for running validators.
    Graph is lazy-loaded only when needed for optimization with large projects (2k+ models).
    """

    manifest: dict = attrs.field(validator=attrs.validators.instance_of(dict))
    profiles: dict = attrs.field(validator=attrs.validators.instance_of(dict))
    dbt_project: dict = attrs.field(validator=attrs.validators.instance_of(dict))
    config: 'Config' = attrs.field()
    _graph: 'DmpAfGraph | None' = attrs.field(default=None, init=False)

    @property
    def graph(self) -> 'DmpAfGraph':
        """Lazy load graph only if needed"""
        if self._graph is None:
            from dmp_af.builder.dmp_af_builder import DmpAfGraph

            self._graph = DmpAfGraph.from_manifest(
                manifest=self.manifest,
                profiles=self.profiles,
                project_profile_name=self.dbt_project['profile'],
                etl_service_name='',
                config=self.config,
            )
        return self._graph
