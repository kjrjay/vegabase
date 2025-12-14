import os
import json
import httpx
from fastapi import Request, Response

class Inertia:
    def __init__(self, app, ssr_url: str = None):
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

    async def render(self, component: str, props: dict, request: Request):
        page_data = {
            "component": component,
            "props": props,
            "url": str(request.url.path),
            "version": "1.0" # TODO: Implement asset hashing
        }

        # CASE A: Client is navigating (AJAX)
        if "X-Inertia" in request.headers:
            return Response(
                content=json.dumps(page_data),
                media_type="application/json",
                headers={"X-Inertia": "true"}
            )

        # CASE B: First Load (Browser Refresh) -> SSR
        head = []
        body = ""
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.ssr_url, json=page_data)
                try:
                    ssr_response = resp.json()
                    head = ssr_response.get('head', [])
                    body = ssr_response.get('body', '')
                except json.JSONDecodeError:
                    # Log error but don't crash, fall back to CSR
                    print(f"SSR JSON Error: {resp.text}")
                    pass
        except Exception as e:
            print(f"SSR Connection Error: {e}")
            body = f"<div id='app' data-page='{json.dumps(page_data)}'></div>"

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

