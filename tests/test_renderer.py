"""
Tests for Renderer modes and caching.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from vegabase.renderer import ReactRenderer, LRUCache


class TestLRUCache:
    """Test LRU cache implementation."""

    def test_cache_stores_and_retrieves(self):
        cache = LRUCache(maxsize=3)
        cache.set("key1", ([], "body1", 1.0))
        
        result = cache.get("key1")
        assert result == ([], "body1", 1.0)

    def test_cache_returns_none_for_missing_key(self):
        cache = LRUCache(maxsize=3)
        result = cache.get("nonexistent")
        assert result is None

    def test_cache_evicts_lru_when_full(self):
        cache = LRUCache(maxsize=2)
        cache.set("key1", ([], "body1", 1.0))
        cache.set("key2", ([], "body2", 2.0))
        cache.set("key3", ([], "body3", 3.0))  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") is not None
        assert cache.get("key3") is not None

    def test_cache_updates_lru_on_get(self):
        cache = LRUCache(maxsize=2)
        cache.set("key1", ([], "body1", 1.0))
        cache.set("key2", ([], "body2", 2.0))
        
        # Access key1 to make it most recently used
        cache.get("key1")
        
        # Add key3 - should evict key2 (now LRU)
        cache.set("key3", ([], "body3", 3.0))
        
        assert cache.get("key1") is not None
        assert cache.get("key2") is None
        assert cache.get("key3") is not None

    def test_cache_pop_removes_key(self):
        cache = LRUCache(maxsize=3)
        cache.set("key1", ([], "body1", 1.0))
        
        result = cache.pop("key1")
        assert result == ([], "body1", 1.0)
        assert cache.get("key1") is None

    def test_cache_clear_removes_all(self):
        cache = LRUCache(maxsize=3)
        cache.set("key1", ([], "body1", 1.0))
        cache.set("key2", ([], "body2", 2.0))
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_contains(self):
        cache = LRUCache(maxsize=3)
        cache.set("key1", ([], "body1", 1.0))
        
        assert "key1" in cache
        assert "key2" not in cache


@pytest.fixture
def mock_request():
    """Create a mock FastAPI request."""
    request = MagicMock()
    request.headers = {}
    request.url.path = "/test"
    request.session = {}
    return request


@pytest.fixture
def renderer():
    """Create a ReactRenderer instance with mocked SSR."""
    app = MagicMock()
    instance = ReactRenderer(app, cache_maxsize=10)
    return instance


class TestRenderModes:
    """Test different rendering modes."""

    @pytest.mark.asyncio
    async def test_ssr_mode_calls_ssr_server(self, renderer, mock_request):
        renderer._ssr_render = AsyncMock(return_value=(["<title>Test</title>"], "<div>SSR</div>"))
        
        response = await renderer.render("TestPage", {"data": "value"}, mock_request, mode="ssr")
        
        renderer._ssr_render.assert_called_once()
        assert response.status_code == 200
        assert "text/html" in response.media_type
        assert "Cache-Control" in response.headers
        assert "no-cache" in response.headers["Cache-Control"]

    @pytest.mark.asyncio
    async def test_client_mode_skips_ssr(self, renderer, mock_request):
        renderer._ssr_render = AsyncMock()
        
        response = await renderer.render("TestPage", {"data": "value"}, mock_request, mode="client")
        
        renderer._ssr_render.assert_not_called()
        body = response.body.decode()
        assert 'id="app"' in body  # Should have #app container
        assert "client.js" in body  # Should include script tag

    @pytest.mark.asyncio
    async def test_cached_mode_caches_result(self, renderer, mock_request):
        renderer._ssr_render = AsyncMock(return_value=([], "<div>Cached</div>"))
        
        # First call - cache miss
        await renderer.render("TestPage", {}, mock_request, mode="cached", revalidate=60)
        assert renderer._ssr_render.call_count == 1
        
        # Second call - cache hit
        await renderer.render("TestPage", {}, mock_request, mode="cached", revalidate=60)
        assert renderer._ssr_render.call_count == 1  # Not called again

    @pytest.mark.asyncio
    async def test_cached_mode_sets_cache_headers(self, renderer, mock_request):
        renderer._ssr_render = AsyncMock(return_value=([], "<div>Cached</div>"))
        
        response = await renderer.render("TestPage", {}, mock_request, mode="cached", revalidate=60)
        
        assert "Cache-Control" in response.headers
        assert "max-age=60" in response.headers["Cache-Control"]
        assert "stale-while-revalidate" in response.headers["Cache-Control"]

    @pytest.mark.asyncio
    async def test_static_mode_no_js(self, renderer, mock_request):
        renderer._ssr_render = AsyncMock(return_value=([], "<div>Static</div>"))
        
        response = await renderer.render("TestPage", {}, mock_request, mode="static")
        
        body = response.body.decode()
        assert "client.js" not in body  # Should NOT include script tag
        assert "<div>Static</div>" in body

    @pytest.mark.asyncio
    async def test_static_mode_sets_cache_headers(self, renderer, mock_request):
        renderer._ssr_render = AsyncMock(return_value=([], "<div>Static</div>"))
        
        response = await renderer.render("TestPage", {}, mock_request, mode="static")
        
        assert "Cache-Control" in response.headers
        assert "public" in response.headers["Cache-Control"]


class TestAjaxRequests:
    """Test AJAX requests (X-Vegabase header)."""

    @pytest.mark.asyncio
    async def test_ajax_request_returns_json(self, renderer, mock_request):
        mock_request.headers = {"X-Vegabase": "true"}
        
        response = await renderer.render("TestPage", {"data": "value"}, mock_request)
        
        assert response.media_type == "application/json"
        assert response.headers.get("X-Vegabase") == "true"


class TestFlashMessages:
    """Test flash message functionality."""

    def test_flash_sets_session(self, renderer, mock_request):
        renderer.flash(mock_request, "Success!", type="success")
        
        assert "_vegabase_flash" in mock_request.session
        assert mock_request.session["_vegabase_flash"]["message"] == "Success!"
        assert mock_request.session["_vegabase_flash"]["type"] == "success"

    def test_flash_raises_without_session(self, renderer):
        request = MagicMock(spec=[])  # No session attribute
        
        with pytest.raises(RuntimeError, match="session middleware"):
            renderer.flash(request, "Error!")

    @pytest.mark.asyncio
    async def test_flash_injected_into_props(self, renderer, mock_request):
        renderer._ssr_render = AsyncMock(return_value=([], "<div>Test</div>"))
        mock_request.session["_vegabase_flash"] = {"type": "success", "message": "Done!"}
        
        await renderer.render("TestPage", {}, mock_request)
        
        # Flash should be cleared from session
        assert "_vegabase_flash" not in mock_request.session


class TestCacheInvalidation:
    """Test cache invalidation."""

    @pytest.mark.asyncio
    async def test_invalidate_cache_clears_specific_key(self, renderer, mock_request):
        renderer._ssr_render = AsyncMock(return_value=([], "<div>Test</div>"))
        
        # Populate cache
        await renderer.render("Page1", {}, mock_request, mode="cached", revalidate=60)
        await renderer.render("Page2", {}, mock_request, mode="cached", revalidate=60)
        
        # Invalidate one key
        renderer.invalidate_cache("Page1")
        
        # Page1 should cause a new SSR call
        renderer._ssr_render.reset_mock()
        await renderer.render("Page1", {}, mock_request, mode="cached", revalidate=60)
        assert renderer._ssr_render.call_count == 1
        
        # Page2 should still be cached
        renderer._ssr_render.reset_mock()
        await renderer.render("Page2", {}, mock_request, mode="cached", revalidate=60)
        assert renderer._ssr_render.call_count == 0

    @pytest.mark.asyncio
    async def test_invalidate_cache_clears_all(self, renderer, mock_request):
        renderer._ssr_render = AsyncMock(return_value=([], "<div>Test</div>"))
        
        # Populate cache
        await renderer.render("Page1", {}, mock_request, mode="cached", revalidate=60)
        await renderer.render("Page2", {}, mock_request, mode="cached", revalidate=60)
        
        # Clear all
        renderer.invalidate_cache()
        
        # Both should cause new SSR calls
        renderer._ssr_render.reset_mock()
        await renderer.render("Page1", {}, mock_request, mode="cached", revalidate=60)
        await renderer.render("Page2", {}, mock_request, mode="cached", revalidate=60)
        assert renderer._ssr_render.call_count == 2
