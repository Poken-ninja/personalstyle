"""Read configuration without connecting to providers or creating storage."""

import re
import tomllib
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Configuration is invalid or unsupported."""


# Required fields and types for the current configuration schema.
FIELDS: dict[str, dict[str, type]] = {
    "project": {"name": str, "environment": str},
    "versions": {
        "protocol": str, "config_schema": int, "storage_schema": int,
        "profile_schema": int, "prompt_contract": int, "compatibility_policy": str,
    },
    "model": {"provider": str, "model": str, "temperature": float, "max_tokens": int},
    "harness": {
        "max_generation_attempts": int, "max_total_model_calls": int, "timeout_seconds": int,
    },
    "context": {"explicit_context_required": bool, "max_examples": int, "max_context_tokens": int},
    "retrieval": {"strategy": str, "embeddings_enabled": bool, "vector_database_enabled": bool},
    "agent": {"enabled": bool, "max_strategy_steps": int},
    "verification": {
        "semantic_required": bool, "required_information_required": bool,
        "constraint_required": bool, "structural_required": bool,
        "context_required": bool, "style_is_hard_gate": bool,
    },
    "storage": {"backend": str, "path": str},
    "security": {
        "companion_mode_enabled": bool, "default_network_scope": str,
        "network_clients_require_auth": bool, "remote_transport_requires_encryption": bool,
        "browser_origin_validation_required": bool, "secrets_in_config_allowed": bool,
        "application_level_storage_encryption": bool,
    },
    "scheduling": {"enabled": bool},
    "logging": {"level": str, "store_prompts": bool, "store_outputs": bool},
}


def load_config(path: Path) -> dict[str, Any]:
    """Validate schema 1 and retain every supplied policy value unchanged."""
    try:
        with path.open("rb") as stream:
            config = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as error:
        # Do not echo potentially sensitive TOML content or parser excerpts.
        raise ConfigError("Configuration cannot be read as TOML") from error
    if config.keys() != FIELDS.keys():
        raise ConfigError("Unsupported or missing configuration section")
    for section, fields in FIELDS.items():
        values = config[section]
        if not isinstance(values, dict) or values.keys() != fields.keys():
            raise ConfigError(f"Unsupported or missing fields in {section}")
        for field, expected_type in fields.items():
            value = values[field]
            if type(value) is not expected_type:
                raise ConfigError(f"Invalid type for {section}.{field}")
            if expected_type is int and isinstance(value, int) and value <= 0:
                raise ConfigError(f"Expected positive value for {section}.{field}")
            if expected_type is str and isinstance(value, str) and not value.strip():
                raise ConfigError(f"Expected nonempty value for {section}.{field}")
    versions = config["versions"]
    for field in ("config_schema", "storage_schema", "profile_schema", "prompt_contract"):
        if versions[field] != 1:
            raise ConfigError(f"Unsupported {field}; no migration is implemented")
    if not re.fullmatch(r"1\.(0|[1-9][0-9]*)", versions["protocol"]):
        raise ConfigError("Unsupported protocol major or malformed protocol version")
    if versions["compatibility_policy"] != "same-major-capability-negotiated":
        raise ConfigError("Unsupported compatibility policy")
    if not 0 <= config["model"]["temperature"] <= 2:
        raise ConfigError("Temperature must be between 0 and 2")
    return config
