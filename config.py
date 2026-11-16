
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def load_config(config_path: Path | None = None) -> dict:
    """Load application settings from a YAML configuration file."""
    config_path = config_path or DEFAULT_CONFIG_PATH

    if not config_path.is_file():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    try:
        with config_path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except yaml.YAMLError as error:
        raise ValueError(
            f"Invalid YAML configuration: {config_path}"
        ) from error

    if not isinstance(config, dict):
        raise ValueError("Configuration must contain a YAML mapping.")

    return config
