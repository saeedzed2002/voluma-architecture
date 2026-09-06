import { NextRequest, NextResponse } from "next/server";

const backendBaseUrl = (
  process.env.VOLUMA_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000"
).replace(/\/$/, "");

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  const headers = new Headers({ "Content-Type": "application/json" });
  for (const header of ["origin", "x-forwarded-for"] as const) {
    const value = request.headers.get(header);
    if (value !== null) headers.set(header, value);
  }
  try {
    const backendResponse = await fetch(`${backendBaseUrl}/api/v1/contact`, {
      body: await request.arrayBuffer(),
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
  } catch {
    return NextResponse.json(
      { detail: "contact service is temporarily unavailable" },
      { headers: { "Cache-Control": "no-store" }, status: 502 },
    );
  }
}
