/** HistorianBridge REST client. Mirrors the FastAPI gateway. */
import type { HistorianPoint, HistorianTag, TagQuery } from "@axon/core";

import { HistorianBridgeError, type ProblemDetails } from "./errors.js";
import { buildQuery } from "./url.js";

export interface HistorianBridgeClientOptions {
    baseUrl: string;
    /** Optional request timeout in ms. Default 30000. */
    timeoutMs?: number;
    /** Override fetch (tests). */
    fetch?: typeof fetch;
    /** Extra headers (auth, tracing). */
    headers?: Record<string, string>;
}

export class HistorianBridgeClient {
    private readonly baseUrl: string;
    private readonly timeoutMs: number;
    private readonly _fetch: typeof fetch;
    private readonly headers: Record<string, string>;

    constructor(opts: HistorianBridgeClientOptions) {
        this.baseUrl = opts.baseUrl.replace(/\/+$/, "");
        this.timeoutMs = opts.timeoutMs ?? 30_000;
        this._fetch = opts.fetch ?? fetch;
        this.headers = { "content-type": "application/json", ...opts.headers };
    }

    async health(): Promise<{ ok: boolean }> {
        return this.request<{ ok: boolean }>("GET", "/healthz");
    }

    async listTags(opts: { prefix?: string; limit?: number } = {}): Promise<HistorianTag[]> {
        return this.request<HistorianTag[]>("GET", `/tags${buildQuery(opts)}`);
    }

    async getCurrent(tags: string[]): Promise<HistorianPoint[]> {
        return this.request<HistorianPoint[]>("GET", `/current${buildQuery({ tag: tags })}`);
    }

    async query(q: TagQuery): Promise<HistorianPoint[]> {
        return this.request<HistorianPoint[]>("POST", "/query", q);
    }

    async write(points: HistorianPoint[]): Promise<{ ok: boolean; n: number }> {
        return this.request<{ ok: boolean; n: number }>("POST", "/write", points);
    }

    private async request<T>(method: string, path: string, body?: unknown): Promise<T> {
        const ctrl = new AbortController();
        const timer = setTimeout(() => ctrl.abort(), this.timeoutMs);
        try {
            const res = await this._fetch(`${this.baseUrl}${path}`, {
                method,
                headers: this.headers,
                body: body === undefined ? undefined : JSON.stringify(body),
                signal: ctrl.signal,
            });
            const text = await res.text();
            const parsed = text ? safeJson(text) : undefined;
            if (!res.ok) {
                const problem: ProblemDetails =
                    parsed && typeof parsed === "object" ? (parsed as ProblemDetails) : { detail: text };
                throw new HistorianBridgeError(res.status, problem);
            }
            return parsed as T;
        } finally {
            clearTimeout(timer);
        }
    }
}

function safeJson(text: string): unknown {
    try {
        return JSON.parse(text);
    } catch {
        return undefined;
    }
}
