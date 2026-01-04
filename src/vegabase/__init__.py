import logging
import logging.config

from .config import settings
from .manifest import Route, RouteManifest
from .middleware import TimingMiddleware
from .renderer import ReactRenderer, RenderMode

__all__ = ["ReactRenderer", "RenderMode", "Route", "RouteManifest", "TimingMiddleware"]

# Convert DynaBox to plain dict for logging.config.dictConfig
logging.config.dictConfig(settings.LOGGING)
