import { NextResponse } from "next/server";

const API_TARGET = process.env.API_TARGET || "http://localhost:8000";

async function handler(request: Request, context: { params: { path: string[] } }) {
  const { path } = context.params;
  const url = new URL(request.url);
  const targetUrl = `${API_TARGET}/${path.join("/")}${url.search}`;

  const headers = new Headers(request.headers);
  headers.delete("host");

  const init: RequestInit = {
    method: request.method,
    headers,
    body: request.method === "GET" || request.method === "HEAD" ? undefined : await request.text(),
  };

  const response = await fetch(targetUrl, init);
  const contentType = response.headers.get("content-type") || "application/json";
  const body = await response.text();

  return new NextResponse(body, {
    status: response.status,
    headers: {
      "content-type": contentType,
    },
  });
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
