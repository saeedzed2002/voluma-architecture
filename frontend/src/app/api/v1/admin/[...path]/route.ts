import { NextRequest, NextResponse } from "next/server";

const backendBaseUrl = (
  process.env.VOLUMA_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000"
).replace(/\/$/, "");

const forwardedHeaders = ["accept", "content-type", "cookie", "origin", "x-voluma-csrf"] as const;

export const dynamic = "force-dynamic";

async function proxyAdminRequest(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  const target = new URL(
    `/api/v1/admin/${path.map((segment) => encodeURIComponent(segment)).join("/")}${request.nextUrl.search}`,
    backendBaseUrl,
  );
  const headers = new Headers();
  for (const header of forwardedHeaders) {
    const value = request.headers.get(header);
    if (value !== null) headers.set(header, value);
  }

  const init: RequestInit = {
    cache: "no-store",
    headers,
    method: request.method,
    redirect: "manual",
  };
  if (request.method !== "GET" && request.method !== "HEAD") {
    const contentType = request.headers.get("content-type") ?? "";
    if (contentType.startsWith("multipart/form-data")) {
      // Rebuild multipart payloads so Undici owns the boundary it advertises to
      // FastAPI. Forwarding an incoming byte stream with its original boundary
      // can otherwise make the `file` field disappear at the upstream parser.
      headers.delete("content-type");
      init.body = await request.formData();
    } else {
      const body = await request.arrayBuffer();
      if (body.byteLength > 0) init.body = body;
    }
  }

  try {
    const backendResponse = await fetch(target, init);
    const responseHeaders = new Headers({ "Cache-Control": "no-store" });
    for (const header of ["content-type", "set-cookie"] as const) {
      const value = backendResponse.headers.get(header);
      if (value !== null) responseHeaders.set(header, value);
    }
    return new NextResponse(await backendResponse.arrayBuffer(), {
      headers: responseHeaders,
      status: backendResponse.status,
    });
  } catch {
    return NextResponse.json(
      { detail: "administrator API is temporarily unavailable" },
      { headers: { "Cache-Control": "no-store" }, status: 502 },
    );
  }
}

export const GET = proxyAdminRequest;
export const POST = proxyAdminRequest;
export const PUT = proxyAdminRequest;
export const PATCH = proxyAdminRequest;
export const DELETE = proxyAdminRequest;
