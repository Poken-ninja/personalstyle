"""Non-generation initialization CLI."""

import logging
from pathlib import Path, PureWindowsPath
from typing import Annotated

import typer

from personalstyle.config import ConfigError, load_config
from personalstyle.security import SecurityError, log_event, prepare_private_directory

app = typer.Typer(help="PersonalStyle initialization tools. Product generation is unavailable.")


@app.command()
def check(
    config: Annotated[Path, typer.Option(help="Path to project configuration")] = Path(
        "personalstyle.toml"
    ),
    prepare_storage: Annotated[
        bool, typer.Option(help="Explicitly prepare an empty OS-protected profile directory")
    ] = False,
) -> None:
    """Validate configuration without an LLM or storage writes."""
    try:
        settings = load_config(config)
        if prepare_storage:
            relative = PureWindowsPath(settings["storage"]["path"])
            directory = config.absolute().parent.joinpath(*relative.parts[:-1])
            prepare_private_directory(directory)
            log_event(logging.getLogger(__name__), "storage_prepared")
    except (ConfigError, SecurityError) as error:
        log_event(logging.getLogger(__name__), "startup_rejected")
        typer.echo(f"Startup check failed: {error}", err=True)
        raise typer.Exit(code=1) from error
    typer.echo("Configuration valid; initialization ready.")
    log_event(logging.getLogger(__name__), "startup_valid")
    if prepare_storage:
        typer.echo("Empty profile directory prepared with verified OS permissions.")
        typer.echo("No application-level encryption; protection relies on the OS account/disk.")
    typer.echo(f"Version declarations: {settings['versions']}")
    if settings["model"]["model"] == "TODO":
        typer.echo("Generation not ready: model is TODO; generation is not implemented.")
    else:
        typer.echo("Generation is not implemented; model readiness is not verified.")
