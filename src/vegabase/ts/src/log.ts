/**
 * Shared logging utilities for SSR servers (dev and prod).
 */

/**
 * Format timestamp with local timezone offset.
 * Example: 2026-01-04T13:49:31+0200
 */
export function formatTimestamp(): string {
    const now = new Date();
    const pad = (n: number, len = 2) => n.toString().padStart(len, '0');
    const tzOffset = -now.getTimezoneOffset();
    const tzSign = tzOffset >= 0 ? '+' : '-';
    const tzHours = pad(Math.floor(Math.abs(tzOffset) / 60));
    const tzMins = pad(Math.abs(tzOffset) % 60);
    return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}${tzSign}${tzHours}${tzMins}`;
}

/**
 * Get status emoji based on HTTP status code.
 */
export function statusEmoji(status: number): string {
    return status >= 500 ? "❌" : status >= 400 ? "⚠️" : "✅";
}

/**
 * Log an SSR request in a consistent format.
 * Example: ✅ 2026-01-04T13:49:31+0200 POST /tickets [Tickets/Show] - 200 (29ms)
 */
export function logRequest(
    method: string,
    url: string,
    component: string | null,
    status: number,
    durationMs: number
): void {
    const emoji = statusEmoji(status);
    const timestamp = formatTimestamp();
    if (component) {
        console.log(`${emoji} ${timestamp} ${method} ${url} [${component}] - ${status} (${durationMs}ms)`);
    } else {
        console.log(`${emoji} ${timestamp} ${method} ${url} - ${status} (${durationMs}ms)`);
    }
}
