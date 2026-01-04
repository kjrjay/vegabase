import render from './ssr.tsx';
import { logRequest } from '__LOG_PATH__';

const port = Number(process.env.PORT) || __DEFAULT_PORT__;

console.log(`Starting TanStack Router SSR server on port ${port}...`);

Bun.serve({
    port,
    async fetch(req) {
        const url = new URL(req.url);
        const startTime = Date.now();

        let response: Response;
        let status = 200;
        let pageInfo: any = null;  // Store page data for logging

        if (req.method === "GET" && url.pathname === "/health") {
            response = Response.json({ status: "OK", timestamp: Date.now() });
            status = response.status;
        } else if (req.method === "GET" && url.pathname === "/shutdown") {
            console.log(`🛑 Shutdown request received`);
            // Schedule exit after response is sent
            setTimeout(() => process.exit(0), 100);
            response = new Response("Shutting down", { status: 200 });
            status = 200;
        } else if (req.method === "POST" && url.pathname === "/render") {
            try {
                const page = await req.json();
                pageInfo = page;  // Store for logging
                const result = await render(page);
                response = Response.json(result);
                status = response.status;
            } catch (error: any) {
                console.error("❌ SSR Error:", error);
                response = Response.json({ error: error.message }, { status: 500 });
                status = 500;
            }
        } else {
            response = new Response("Not Found", { status: 404 });
            status = 404;
        }

        // Log request
        const duration = Date.now() - startTime;
        if (pageInfo) {
            logRequest(req.method, pageInfo.url, pageInfo.component, status, duration);
        } else {
            logRequest(req.method, url.pathname, null, status, duration);
        }

        return response;
    },
});
