"""Non-generation initialization CLI."""

import json
import logging
from pathlib import Path, PureWindowsPath
from typing import Annotated

import typer

from personalstyle.config import ConfigError, load_config
from personalstyle.profile import derive_writing_dna
from personalstyle.security import SecurityError, log_event, prepare_private_directory
from personalstyle.storage import MAX_TEXT_BYTES, ExampleInput, ExampleStore, StoreError

app = typer.Typer(help="PersonalStyle initialization tools. Product generation is unavailable.")


@app.command()
def check(
    config: Annotated[Path, typer.Option(help="Path to project configuration")] = Path(
        "personalstyle.toml"
    ),
    prepare_storage: Annotated[
        bool, typer.Option(help="Explicitly prepare an empty OS-protected profile directory")
    ] = False,
    add_example: Annotated[Path | None, typer.Option(help="Bounded JSON example request file")] = None,
    get_example: Annotated[str | None, typer.Option(help="Explicitly print a stored example UUID")] = None,
    writing_dna: Annotated[
        str | None, typer.Option(help="Inspect derived Writing DNA for one exact context")
    ] = None,
) -> None:
    """Validate configuration without an LLM or storage writes."""
    try:
        settings = load_config(config)
        relative = PureWindowsPath(settings["storage"]["path"])
        if sum((prepare_storage, add_example is not None, get_example is not None,
                writing_dna is not None)) > 1:
            raise StoreError("INVALID_EXAMPLE")
        if add_example is not None or get_example is not None or writing_dna is not None:
            store = ExampleStore(config.absolute().parent.joinpath(*relative.parts))
            if writing_dna is not None:
                snapshot = derive_writing_dna(
                    store, writing_dna, profile_schema=settings["versions"]["profile_schema"],
                    timeout_seconds=settings["harness"]["timeout_seconds"],
                )
                typer.echo(json.dumps(snapshot, ensure_ascii=False))
            elif add_example is not None:
                try:
                    with add_example.open("rb") as stream:
                        payload = stream.read(MAX_TEXT_BYTES + 4097)
                    if len(payload) > MAX_TEXT_BYTES + 4096:
                        raise StoreError("INVALID_EXAMPLE")
                    request = json.loads(payload)
                    if not isinstance(request, dict) or request.keys() != {
                        "id", "text", "context", "supplier", "authorizer", "source_kind",
                        "authorized", "learning_eligible", "held_out",
                    }:
                        raise StoreError("INVALID_EXAMPLE")
                    record = store.add(ExampleInput(**request))
                except (OSError, UnicodeError, json.JSONDecodeError, TypeError):
                    raise StoreError("INVALID_EXAMPLE") from None
                typer.echo(f"Example stored: {record['id']}")
            else:
                inspected = store.get(get_example or "")
                # Explicit inspection is user-requested output, never ordinary telemetry.
                typer.echo(json.dumps(inspected, ensure_ascii=False))
            return
        if prepare_storage:
            relative = PureWindowsPath(settings["storage"]["path"])
            directory = config.absolute().parent.joinpath(*relative.parts[:-1])
            prepare_private_directory(directory)
            log_event(logging.getLogger(__name__), "storage_prepared")
    except (ConfigError, SecurityError, StoreError) as error:
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
