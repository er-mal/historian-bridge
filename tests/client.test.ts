import { describe, expect, it, vi } from "vitest";

import { HistorianBridgeClient } from "../src/client";
import { HistorianBridgeError } from "../src/errors";

function mockFetch(handler: (url: string, init: RequestInit) => Response | Promise<Response>) {
    return vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = typeof input === "string" ? input : input.toString();
        return handler(url, init ?? {});
    }) as unknown as typeof fetch;
}

const baseUrl = "http://gw.test";

describe("HistorianBridgeClient", () => {
    it("listTags builds prefix query string", async () => {
        const fetchMock = mockFetch((url) => {
            expect(url).toBe("http://gw.test/tags?prefix=site.line1&limit=10");
            return new Response(JSON.stringify([{ name: "site.line1.x" }]), { status: 200 });
        });
        const client = new HistorianBridgeClient({ baseUrl, fetch: fetchMock });
        const tags = await client.listTags({ prefix: "site.line1", limit: 10 });
        expect(tags).toEqual([{ name: "site.line1.x" }]);
    });

    it("getCurrent encodes repeated tag params", async () => {
        const fetchMock = mockFetch((url) => {
            expect(url).toBe("http://gw.test/current?tag=a&tag=b");
            return new Response(JSON.stringify([]), { status: 200 });
        });
        const client = new HistorianBridgeClient({ baseUrl, fetch: fetchMock });
        await client.getCurrent(["a", "b"]);
        expect(fetchMock).toHaveBeenCalledOnce();
    });

    it("query POSTs body and returns points", async () => {
        const fetchMock = mockFetch((url, init) => {
            expect(url).toBe("http://gw.test/query");
            expect(init.method).toBe("POST");
            const body = JSON.parse(String(init.body));
            expect(body.from).toBe("2026-01-01T00:00:00+00:00");
            return new Response(
                JSON.stringify([{ tag: "a", ts: "2026-01-01T00:00:00+00:00", value: 1.0 }]),
                { status: 200 },
            );
        });
        const client = new HistorianBridgeClient({ baseUrl, fetch: fetchMock });
        const out = await client.query({
            tags: ["a"],
            from: "2026-01-01T00:00:00+00:00",
            to: "2026-01-01T01:00:00+00:00",
            agg: "avg",
            interval: "10m",
        });
        expect(out).toHaveLength(1);
    });

    it("non-2xx responses raise HistorianBridgeError with problem details", async () => {
        const fetchMock = mockFetch(() =>
            new Response(JSON.stringify({ title: "bad_request", status: 400, detail: "tags empty" }), {
                status: 400,
            }),
        );
        const client = new HistorianBridgeClient({ baseUrl, fetch: fetchMock });
        await expect(
            client.query({ tags: [], from: "x", to: "y" }),
        ).rejects.toBeInstanceOf(HistorianBridgeError);
    });

    it("write returns ok envelope", async () => {
        const fetchMock = mockFetch(() =>
            new Response(JSON.stringify({ ok: true, n: 2 }), { status: 200 }),
        );
        const client = new HistorianBridgeClient({ baseUrl, fetch: fetchMock });
        const out = await client.write([
            { tag: "a", ts: "2026-01-01T00:00:00+00:00", value: 1 },
            { tag: "a", ts: "2026-01-01T00:00:30+00:00", value: 2 },
        ]);
        expect(out).toEqual({ ok: true, n: 2 });
    });
});
