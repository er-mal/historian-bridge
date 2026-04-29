/** Tiny query-string helper. No deps. */
export function buildQuery(params: Record<string, string | number | string[] | undefined>): string {
    const parts: string[] = [];
    for (const [k, v] of Object.entries(params)) {
        if (v === undefined) continue;
        if (Array.isArray(v)) {
            for (const item of v) parts.push(`${encodeURIComponent(k)}=${encodeURIComponent(item)}`);
        } else {
            parts.push(`${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`);
        }
    }
    return parts.length ? `?${parts.join("&")}` : "";
}
