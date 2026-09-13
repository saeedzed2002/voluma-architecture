import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { POST } from "./route";

describe("contact BFF", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("rejects an oversized body before forwarding it to the backend", async () => {
    const upstream = vi.fn<typeof fetch>();
    vi.stubGlobal("fetch", upstream);
    const request = new NextRequest("https://voluma.example/api/v1/contact", {
      body: "x".repeat(64 * 1024 + 1),
      headers: { "content-length": String(64 * 1024 + 1) },
      method: "POST",
    });

    const response = await POST(request);

    expect(response.status).toBe(413);
    expect(await response.json()).toEqual({ detail: "contact request is too large" });
    expect(upstream).not.toHaveBeenCalled();
  });
});
