import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { POST } from "./route";

describe("administrator BFF", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("rebuilds multipart uploads so the upstream owns the boundary", async () => {
    let forwarded: { init?: RequestInit; target: RequestInfo | URL } | undefined;
    const upstream: typeof fetch = async (target, init) => {
      forwarded = { init, target };
      return new Response(JSON.stringify({ id: "media-id" }), {
        headers: { "content-type": "application/json" },
        status: 202,
      });
    };
    vi.stubGlobal("fetch", upstream);

    const body = new FormData();
    body.append("file", new Blob(["image-data"], { type: "image/png" }), "proof.png");
    const request = new NextRequest("https://voluma.example/api/v1/admin/media", {
      body,
      headers: {
        origin: "https://voluma.example",
        "x-voluma-csrf": "csrf-token",
      },
      method: "POST",
    });

    const response = await POST(request, { params: Promise.resolve({ path: ["media"] }) });

    expect(response.status).toBe(202);
    expect(forwarded).toBeDefined();
    if (forwarded === undefined) throw new Error("administrator BFF did not call the upstream API");
    expect(String(forwarded.target)).toBe("http://127.0.0.1:8000/api/v1/admin/media");
    expect(forwarded.init?.headers).toBeInstanceOf(Headers);
    expect((forwarded.init?.headers as Headers).get("content-type")).toBeNull();
    expect(forwarded.init?.body).toBeInstanceOf(FormData);
    expect((forwarded.init?.body as FormData).get("file")).toBeInstanceOf(Blob);
  });
});
