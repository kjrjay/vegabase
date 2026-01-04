"""
Request timing middleware for uvicorn/ASGI applications.

Logs request duration since uvicorn's built-in logging doesn't include it.
"""

import logging
import time

# Use vegabase logger to avoid uvicorn's AccessFormatter which expects specific attributes
log = logging.getLogger("vegabase.access")


class TimingMiddleware:
    """
    ASGI middleware that logs request timing.
    uvicorn's AccessFormatter doesn't include request duration,
    so we use this instead.

    Usage:
        app.add_middleware(TimingMiddleware)
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()

        # Track status code from response
        status_code = 200

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
            await send(message)

        await self.app(scope, receive, send_wrapper)

        duration_ms = (time.perf_counter() - start) * 1000
        method = scope.get("method", "")
        path = scope.get("path", "")

        # Use same emoji convention as Bun server
        emoji = "❌" if status_code >= 500 else "⚠️" if status_code >= 400 else "✅"

        log.info(f"{emoji} {method} {path} - {status_code} ({duration_ms:.0f}ms)")
