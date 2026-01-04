import os
from pathlib import Path

from dynaconf import Dynaconf, Validator

# Set default environment to development if not specified
# This allows [default] to be used for production/staging/qa
# while still defaulting to development for local work
if "VEGABASE_APP_ENV" not in os.environ:
    os.environ["VEGABASE_APP_ENV"] = "development"

# Get the directory where this file is located (vegabase package dir)
BASE_DIR = Path(__file__).parent
DEFAULT_SETTINGS_PATH = BASE_DIR / "default_settings.yaml"

settings = Dynaconf(
    envvar_prefix="VEGABASE",
    # Load default settings from the library package first
    preload=[str(DEFAULT_SETTINGS_PATH)],
    # Load user settings from the current working directory
    # Order matters: later files override earlier ones
    settings_files=[
        "settings.toml",
        "settings.yaml",
        ".secrets.toml",
        ".secrets.yaml",
        "settings.local.toml",
        "settings.local.yaml",
    ],
    # Enable environment layering (e.g. [development], [production])
    environments=True,
    # Switch environment using VEGABASE_APP_ENV
    env_switcher="VEGABASE_APP_ENV",
    load_dotenv=True,
)

# Ensure critical settings exist
settings.validators.register(
    Validator("SSR_URL", must_exist=True),
    Validator("ASSETS_URL", must_exist=True),
    Validator("LOGGING", must_exist=True),
)

settings.validators.validate()
