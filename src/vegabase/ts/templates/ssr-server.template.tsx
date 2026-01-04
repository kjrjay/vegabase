import render from './ssr.tsx';

const port = Number(process.env.PORT) || __DEFAULT_PORT__;

console.log(`Starting TanStack Router SSR server on port ${port}...`);

Bun.serve({
    port,
    async fetch(req) {
        const url = new URL(req.url);

        if (req.method === "GET" && url.pathname === "/health") {
            return Response.json({ status: "OK", timestamp: Date.now() });
        }

        if (req.method === "GET" && url.pathname === "/shutdown") {
            process.exit(0);
        }

        if (req.method === "POST" && url.pathname === "/render") {
            try {
                const page = await req.json();
                const result = await render(page);
                return Response.json(result);
            } catch (error: any) {
                console.error("SSR Error:", error);
                return Response.json({ error: error.message }, { status: 500 });
            }
        }

        return new Response("Not Found", { status: 404 });
    },
});
