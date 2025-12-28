"""Tests for route manifest module."""

import json
import tempfile
from pathlib import Path

import pytest

from vegabase.manifest import Route, RouteManifest


class TestRoute:
    def test_basic_route(self):
        route = Route(path="/dashboard", component="Dashboard")
        d = route.to_dict()
        assert d["path"] == "/dashboard"
        assert d["component"] == "Dashboard"
        assert d["cacheTime"] == 0
        assert d["preload"] == "intent"

    def test_route_with_options(self):
        route = Route(
            path="/tasks",
            component="Tasks/Index",
            cache_time=60,
            preload="viewport",
        )
        d = route.to_dict()
        assert d["cacheTime"] == 60
        assert d["preload"] == "viewport"

    def test_path_param_normalization(self):
        """Path params should be converted from :id to $id format."""
        route = Route(path="/tasks/:id", component="Tasks/Show")
        assert route.to_dict()["path"] == "/tasks/$id"

    def test_multiple_path_params(self):
        route = Route(path="/users/:userId/tasks/:taskId", component="UserTask")
        assert route.to_dict()["path"] == "/users/$userId/tasks/$taskId"


class TestRouteManifest:
    def test_add_routes(self):
        manifest = RouteManifest()
        manifest.add("/", "Home")
        manifest.add("/about", "About")

        assert len(manifest.routes) == 2
        assert manifest.routes[0].component == "Home"
        assert manifest.routes[1].component == "About"

    def test_method_chaining(self):
        manifest = (
            RouteManifest()
            .add("/", "Home")
            .add("/tasks", "Tasks/Index")
            .add("/tasks/:id", "Tasks/Show", cache_time=30)
        )
        assert len(manifest.routes) == 3

    def test_to_json(self):
        manifest = RouteManifest()
        manifest.add("/", "Dashboard", cache_time=60)

        data = json.loads(manifest.to_json())
        assert data["version"] == 1
        assert len(data["routes"]) == 1
        assert data["routes"][0]["path"] == "/"
        assert data["routes"][0]["component"] == "Dashboard"
        assert data["routes"][0]["cacheTime"] == 60

    def test_save_and_load(self, tmp_path: Path):
        manifest = RouteManifest()
        manifest.add("/", "Home")
        manifest.add("/tasks/:id", "Tasks/Show")

        # Save
        output_file = tmp_path / ".vegabase" / "routes.json"
        manifest.save(output_file)
        assert output_file.exists()

        # Load
        loaded = RouteManifest.load(output_file)
        assert len(loaded.routes) == 2
        assert loaded.routes[0].path == "/"
        assert loaded.routes[1].path == "/tasks/:id"  # Original format preserved internally

    def test_from_json(self):
        json_str = """
        {
            "version": 1,
            "routes": [
                {"path": "/tasks/$id", "component": "Tasks/Show", "cacheTime": 30, "preload": "intent"}
            ]
        }
        """
        manifest = RouteManifest.from_json(json_str)
        assert len(manifest.routes) == 1
        # $id converted back to :id internally
        assert manifest.routes[0].path == "/tasks/:id"
        assert manifest.routes[0].cache_time == 30

    def test_creates_parent_directories(self, tmp_path: Path):
        manifest = RouteManifest().add("/", "Home")
        deep_path = tmp_path / "deep" / "nested" / "routes.json"
        manifest.save(deep_path)
        assert deep_path.exists()
