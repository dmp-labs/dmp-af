"""Dagger module for dmp-af documentation management."""

import typing as tp

import dagger
from dagger import DefaultPath, Doc, dag, function, object_type


@object_type
class Docs:
    """Documentation management for dmp-af project."""

    @staticmethod
    def _get_docs_container(
        source: dagger.Directory,
    ) -> dagger.Container:
        """
        Create a base container with MkDocs and dependencies installed.
        """
        return (
            dag.container()
            .from_('python:3.12-slim')
            .with_exec(['pip', 'install', '--upgrade', 'pip'])
            .with_exec(['pip', 'install', 'uv'])
            .with_directory('/work', source)
            .with_workdir('/work')
            .with_exec(['uv', 'sync', '--group=docs'])
        )

    @function
    async def serve(
        self,
        source: tp.Annotated[
            dagger.Directory,
            DefaultPath('/'),
            Doc('dmp-af source directory'),
        ],
        port: int = 8000,
    ) -> dagger.Service:
        """
        Start local documentation development server with live reload.

        Args:
            source: dmp-af source directory
            port: Port to serve on (default: 8000)

        Returns:
            Service running MkDocs dev server

        Example:
            dagger call serve up --port=8000:8000
        """
        return (
            self._get_docs_container(source)
            .with_exposed_port(port)
            .as_service(args=['uv', 'run', 'mkdocs', 'serve', '--dev-addr', f'0.0.0.0:{port}'])
        )

    @function
    async def build(
        self,
        source: tp.Annotated[
            dagger.Directory,
            DefaultPath('/'),
            Doc('dmp-af source directory'),
        ],
        strict: bool = False,
    ) -> dagger.Directory:
        """
        Build static documentation site.

        Args:
            source: dmp-af source directory
            strict: Enable strict mode (fail on warnings)

        Returns:
            Directory containing built static site

        Example:
            dagger call build export --path=./site
            dagger call build --strict=true export --path=./site
        """
        cmd = ['uv', 'run', 'mkdocs', 'build']
        if strict:
            cmd.append('--strict')

        return await self._get_docs_container(source).with_exec(cmd).directory('/work/site')

    @function
    async def test(
        self,
        source: tp.Annotated[
            dagger.Directory,
            DefaultPath('/'),
            Doc('dmp-af source directory'),
        ],
    ) -> str:
        """
        Test documentation build (strict mode with validation).

        Args:
            source: dmp-af source directory

        Returns:
            Test success message

        Example:
            dagger call test
        """
        await self.build(source, strict=True)
        return 'Documentation build test passed (no warnings or errors)'
