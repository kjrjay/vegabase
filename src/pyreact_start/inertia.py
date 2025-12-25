import json
import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

import httpx
from fastapi import Request, Response


class InertiaJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Pydantic models and common Python types."""

    def default(self, obj: Any) -> Any:  # type: ignore[override]
        # Handle Pydantic models (v2)
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        # Handle Pydantic models (v1 fallback)
        if hasattr(obj, "dict") and hasattr(obj, "__fields__"):
            return obj.dict()
        # Handle dataclasses
        if hasattr(obj, "__dataclass_fields__"):
            from dataclasses import asdict

            return asdict(obj)
        # Handle datetime
        if isinstance(obj, datetime):
            return obj.isoformat()
        # Handle date
        if isinstance(obj, date):
            return obj.isoformat()
        # Handle UUID
        if isinstance(obj, UUID):
            return str(obj)
        # Handle Decimal
        if isinstance(obj, Decimal):
            return float(obj)
        # Handle bytes
        if isinstance(obj, bytes):
            return obj.decode("utf-8", errors="replace")
        # Handle sets
        if isinstance(obj, set):
            return list(obj)

        # Provide helpful error messages for common problematic types
        type_name = type(obj).__name__
        module = type(obj).__module__

        hints = {
            "function": "Functions cannot be serialized. Remove it from props.",
            "method": "Methods cannot be serialized. Remove it from props.",
            "generator": "Convert generator to list() before passing to render().",
            "coroutine": "Await the coroutine before passing to render().",
            "Connection": "Pass data, not database connections.",
            "Session": "Pass data, not database sessions.",
            "Engine": "Pass data, not database engines.",
        }

        hint = hints.get(type_name, "")
        if not hint and "sqlalchemy" in module.lower():
            hint = "SQLAlchemy objects must be converted to Pydantic models or dicts."

        error_msg = f"Object of type '{type_name}' is not JSON serializable."
        if hint:
            error_msg += f" Hint: {hint}"

        raise TypeError(error_msg)


def _serialize(data: Any) -> str:
    """Serialize data to JSON using custom encoder."""
    return json.dumps(data, cls=InertiaJSONEncoder)


class Inertia:
    FLASH_SESSION_KEY = "_inertia_flash"

    def __init__(self, app, ssr_url: str | None = None):
        self.app = app
        self.is_dev = os.getenv("APP_ENV") == "development"

        # Configure SSR URL
        if ssr_url:
            self.ssr_url = ssr_url
        elif self.is_dev:
            self.ssr_url = "http://localhost:3001/render"
        else:
            self.ssr_url = "http://localhost:13714/render"

        # Configure asset paths based on environment
        self.assets_url = "http://localhost:3001" if self.is_dev else "/static/dist"

    def flash(self, request: Request, message: str, type: str = "success") -> None:
        """
        Set a flash message to be displayed on the next page render.

        Args:
            request: The FastAPI request object (must have session middleware)
            message: The flash message text
            type: The message type (success, error, warning, info)
        """
        if not hasattr(request, "session"):
            raise RuntimeError(
                "Flash messages require session middleware. "
                "Add SessionMiddleware to your app:\n\n"
                "  from starlette.middleware.sessions import SessionMiddleware\n"
                "  app.add_middleware(SessionMiddleware, secret_key='your-secret')"
            )
        request.session[self.FLASH_SESSION_KEY] = {"type": type, "message": message}

    def _get_and_clear_flash(self, request: Request) -> dict | None:
        """Get flash message from session and clear it."""
        if not hasattr(request, "session"):
            return None
        return request.session.pop(self.FLASH_SESSION_KEY, None)

    async def render(self, component: str, props: dict, request: Request):
        # Automatically inject flash message if present
        flash = self._get_and_clear_flash(request)
        if flash:
            props = {**props, "flash": flash}

        page_data = {
            "component": component,
            "props": props,
            "url": str(request.url.path),
            "version": "1.0",  # TODO: Implement asset hashing
        }

        # CASE A: Client is navigating (AJAX)
        if "X-Inertia" in request.headers:
            return Response(
                content=_serialize(page_data),
                media_type="application/json",
                headers={"X-Inertia": "true"},
            )

        # CASE B: First Load (Browser Refresh) -> SSR
        head = []
        body = ""

        try:
            async with httpx.AsyncClient() as client:
                # Serialize page_data with custom encoder before sending to SSR
                page_json = json.loads(_serialize(page_data))
                resp = await client.post(self.ssr_url, json=page_json)
                try:
                    ssr_response = resp.json()
                    head = ssr_response.get("head", [])
                    body = ssr_response.get("body", "")
                except json.JSONDecodeError:
                    # Log error but don't crash, fall back to CSR
                    print(f"SSR JSON Error: {resp.text}")
                    pass
        except Exception as e:
            print(f"SSR Connection Error: {e}")
            body = f"<div id='app' data-page='{_serialize(page_data)}'></div>"

        # Construct HTML
        head_html = "\n".join(head) if isinstance(head, list) else str(head)

        # Determine asset URLs
        script_src = f"{self.assets_url}/client.js"
        css_src = f"{self.assets_url}/client.css"

        html = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0" />
            {head_html}
            <title>PyReact App</title>
            <link rel="stylesheet" href="{css_src}" />
          </head>
          <body>
            {body}
            <script type="module" src="{script_src}"></script>
          </body>
        </html>
        """
        return Response(content=html, media_type="text/html")
