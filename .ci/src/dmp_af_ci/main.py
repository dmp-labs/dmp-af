from dagger import function, object_type

from .docs import Docs  # noqa: TID252
from .integration_tests import IntegrationTests  # noqa: TID252


@object_type
class DmpAfCi:
    @function
    def docs(self) -> Docs:
        return Docs()

    @function
    def tests(self) -> IntegrationTests:
        return IntegrationTests()
