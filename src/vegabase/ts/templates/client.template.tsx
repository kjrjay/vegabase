import { hydrateRoot, createRoot } from 'react-dom/client';
import { RouterClient } from '@tanstack/react-router/ssr/client';
import { RouterProvider } from '@tanstack/react-router';
import { createRouter, createClientRouter } from './routeTree.gen';

// Hot Reload Logic - Only included in development builds
if (process.env.NODE_ENV !== 'production' && typeof window !== 'undefined' && window.location.hostname === "localhost") {
    const ws = new WebSocket("ws://localhost:__WS_PORT__/ws");
    ws.onmessage = (event) => {
        if (event.data === "reload") {
            console.log("♻️ Refreshing...");
            window.location.reload();
        }
    };
}

// Check if SSR dehydration data exists (set by Scripts component via streaming SSR)
if (typeof window !== 'undefined' && (window as any).$_TSR) {
    // SSR mode: Hydrate entire document with RouterClient (streaming SSR)
    console.log("🔥 Hydrating SSR page");
    const router = createRouter();
    hydrateRoot(document, <RouterClient router={router} />);
} else {
    // Client-only mode: Mount into #app using client router
    console.log("📦 Client-side render");
    const appElement = document.getElementById('app');
    if (appElement) {
        const clientRouter = createClientRouter();
        createRoot(appElement).render(<RouterProvider router={clientRouter} />);
    }
}
