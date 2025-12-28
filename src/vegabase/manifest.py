"""Route manifest for TanStack Router integration.

This module provides a way to define routes in Python and export them
for the vegabase CLI to generate a typed TanStack Router route tree.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass
class Route:
    """A route definition for TanStack Router.

    Attributes:
        path: URL path pattern (e.g., "/tasks/:id" or "/users/$userId")
        component: React component path relative to frontend/pages (e.g., "Tasks/Show")
        cache_time: Client-side cache TTL in seconds. 0 = no caching.
        preload: When to preload route data.
            - "intent": Preload on hover (default)
            - "viewport": Preload when link enters viewport
            - "render": Preload immediately when parent renders
    """

    path: str
    component: str
    cache_time: int = 0
    preload: Literal["intent", "viewport", "render"] = "intent"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": self._normalize_path(self.path),
            "component": self.component,
            "cacheTime": self.cache_time,
            "preload": self.preload,
        }

    def _normalize_path(self, path: str) -> str:
        """Convert path params from :id to $id format (TanStack Router style)."""
        import re

        return re.sub(r":(\w+)", r"$\1", path)


@dataclass
class RouteManifest:
    """Collection of routes for TanStack Router generation.

    Usage:
        routes = RouteManifest()
        routes.add("/", "Dashboard", cache_time=60)
        routes.add("/tasks", "Tasks/Index")
        routes.add("/tasks/:id", "Tasks/Show")
        routes.save()  # Writes to .vegabase/routes.json
    """

    routes: list[Route] = field(default_factory=list)

    def add(
        self,
        path: str,
        component: str,
        *,
        cache_time: int = 0,
        preload: Literal["intent", "viewport", "render"] = "intent",
    ) -> "RouteManifest":
        """Add a route to the manifest.

        Args:
            path: URL path pattern (use :param for path parameters)
            component: React component path relative to frontend/pages
            cache_time: Client-side cache TTL in seconds (0 = no caching)
            preload: Preload strategy ("intent", "viewport", or "render")

        Returns:
            Self for method chaining
        """
        self.routes.append(
            Route(
                path=path,
                component=component,
                cache_time=cache_time,
                preload=preload,
            )
        )
        return self

    def to_dict(self) -> dict:
        """Convert manifest to dictionary for JSON serialization."""
        return {
            "version": 1,
            "routes": [route.to_dict() for route in self.routes],
        }

    def to_json(self, indent: int = 2) -> str:
        """Export manifest as JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, path: str | Path = ".vegabase/routes.json") -> Path:
        """Write manifest to disk.

        Args:
            path: Output path (default: .vegabase/routes.json)

        Returns:
            Path to the written file
        """
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_json())
        return output_path

    @classmethod
    def from_json(cls, json_str: str) -> "RouteManifest":
        """Load manifest from JSON string."""
        data = json.loads(json_str)
        manifest = cls()
        for route_data in data.get("routes", []):
            # Convert $param back to :param for internal representation
            import re

            path = re.sub(r"\$(\w+)", r":\1", route_data["path"])
            manifest.add(
                path=path,
                component=route_data["component"],
                cache_time=route_data.get("cacheTime", 0),
                preload=route_data.get("preload", "intent"),
            )
        return manifest

    @classmethod
    def load(cls, path: str | Path = ".vegabase/routes.json") -> "RouteManifest":
        """Load manifest from disk.

        Args:
            path: Path to manifest file

        Returns:
            Loaded RouteManifest instance
        """
        return cls.from_json(Path(path).read_text())
