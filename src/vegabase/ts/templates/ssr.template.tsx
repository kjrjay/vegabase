import { createRequestHandler, defaultStreamHandler } from '@tanstack/react-router/ssr/server';
import { createRouter, setSSRProps, setSSRMode } from './routeTree.gen';

export default async function render(page: {
    component: string;
    props: any;
    url: string;
    mode?: string;
}) {
    // Set SSR mode and props before rendering
    setSSRMode(page.mode || 'ssr');
    setSSRProps(page.props);

    // Create request for the URL
    const request = new Request(`http://localhost${page.url}`, { method: 'GET' });

    // Use TanStack's SSR handler - this handles dehydration via Scripts component
    const handler = createRequestHandler({ request, createRouter });
    const response = await handler(defaultStreamHandler);

    // Read the streaming response
    const html = await response.text();

    // Return full HTML document (Python should NOT wrap this)
    return { head: [], body: html };
}
