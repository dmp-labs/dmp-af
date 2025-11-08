import typer

app = typer.Typer()


@app.callback()
def callback():
    """
    dmp-af CLI - Tools for dbt project validation and management.
    """
    pass


from dmp_af.cli import validate  # noqa: E402, F401
