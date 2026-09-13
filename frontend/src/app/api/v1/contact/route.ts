import { NextRequest, NextResponse } from "next/server";

const backendBaseUrl = (
  process.env.VOLUMA_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000"
).replace(/\/$/, "");
const maxContactRequestBytes = 64 * 1024;

export const dynamic = "force-dynamic";

class ContactRequestTooLargeError extends Error {}

async function readContactRequestBody(request: NextRequest): Promise<ArrayBuffer> {
  const declaredLength = Number(request.headers.get("content-length"));
  if (Number.isFinite(declaredLength) && declaredLength > maxContactRequestBytes) {
    throw new ContactRequestTooLargeError();
  }
  if (request.body === null) return new ArrayBuffer(0);

  const reader = request.body.getReader();
  const chunks: Uint8Array[] = [];
  let length = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      length += value.byteLength;
      if (length > maxContactRequestBytes) throw new ContactRequestTooLargeError();
      chunks.push(value);
    }
  } catch (error) {
    await reader.cancel(error);
    throw error;
  } finally {
    reader.releaseLock();
  }

  const body = new Uint8Array(length);
  let offset = 0;
  for (const chunk of chunks) {
    body.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return body.buffer;
}

export async function POST(request: NextRequest) {
  const headers = new Headers({ "Content-Type": "application/json" });
  for (const header of ["origin", "x-forwarded-for"] as const) {
    const value = request.headers.get(header);
    if (value !== null) headers.set(header, value);
  }
  try {
    const body = await readContactRequestBody(request);
    const backendResponse = await fetch(`${backendBaseUrl}/api/v1/contact`, {
      body,
      cache: "no-store",
      headers,
      method: "POST",
    });
    return new NextResponse(await backendResponse.arrayBuffer(), {
      headers: {
        "Cache-Control": "no-store",
        "Content-Type": backendResponse.headers.get("content-type") ?? "application/json",
      },
      status: backendResponse.status,
    });
  } catch (error) {
    if (error instanceof ContactRequestTooLargeError) {
      return NextResponse.json(
        { detail: "contact request is too large" },
        { headers: { "Cache-Control": "no-store" }, status: 413 },
      );
    }
    return NextResponse.json(
      { detail: "contact service is temporarily unavailable" },
      { headers: { "Cache-Control": "no-store" }, status: 502 },
    );
  }
}
