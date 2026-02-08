from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class ServiceConfig:
    values: Dict[str, Any]


def _coerce_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none", "~"}:
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def parse_env_file(path: str | Path) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = _coerce_scalar(value.strip())
    return data


def parse_simple_yaml(path: str | Path) -> Dict[str, Any]:
    """
    Minimal YAML parser for simple key: value pairs.
    Supports comments (#) and scalar values only.
    """
    data: Dict[str, Any] = {}
    for raw in Path(path).read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = _coerce_scalar(value.strip())
    return data


def merge_config(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    merged.update(overrides)
    return merged


def load_service_config(env_path: str | Path, yaml_path: str | Path) -> ServiceConfig:
    env_values = parse_env_file(env_path)
    yaml_values = parse_simple_yaml(yaml_path)
    return ServiceConfig(values=merge_config(yaml_values, env_values))


def load_service_config_from_files(
    env_path: str | Path, yaml_paths: list[str | Path]
) -> ServiceConfig:
    merged_yaml: Dict[str, Any] = {}
    for path in yaml_paths:
        merged_yaml = merge_config(merged_yaml, parse_simple_yaml(path))
    env_values = parse_env_file(env_path)
    return ServiceConfig(values=merge_config(merged_yaml, env_values))


def parse_service_args(argv: list[str]) -> ServiceConfig:
    """
    Parse service CLI arguments and return a merged configuration.
    --env points to an env file.
    --conf can be provided multiple times to layer configs.
    Later --conf files override earlier ones.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--env", required=True, help="Path to .env file")
    parser.add_argument(
        "--conf",
        action="append",
        default=[],
        help="Path to a config file (repeatable)",
    )
    args = parser.parse_args(argv)
    if not args.conf:
        raise ValueError("at least one --conf must be provided")
    return load_service_config_from_files(args.env, args.conf)
