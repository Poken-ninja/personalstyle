"""Non-generation initialization CLI."""

from pathlib import Path
from typing import Annotated

import typer

from personalstyle.config import ConfigError, load_config

app = typer.Typer(help="PersonalStyle initialization tools. Product generation is unavailable.")


@app.command()
def check(
    config: Annotated[Path, typer.Option(help="Path to project configuration")] = Path(
        "personalstyle.toml"
    ),
) -> None:
    """Validate configuration without an LLM or storage writes."""
    try:
        settings = load_config(config)
    except ConfigError as error:
        typer.echo(f"Startup check failed: {error}", err=True)
        raise typer.Exit(code=1) from error
    typer.echo("Configuration valid; initialization ready.")
    typer.echo(f"Version declarations: {settings['versions']}")
    if settings["model"]["model"] == "TODO":
        typer.echo("Generation not ready: model is TODO; generation is not implemented.")
    else:
        typer.echo("Generation is not implemented; model readiness is not verified.")
