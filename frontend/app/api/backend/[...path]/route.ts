import { NextRequest, NextResponse } from 'next/server';

const backendBase = process.env.BACKEND_BASE_URL || 'http://backend:8000';
const authUser = process.env.BASIC_AUTH_USER || 'admin';
const authPass = process.env.BASIC_AUTH_PASS || 'admin';

const buildAuthHeader = () => {
  const token = Buffer.from(`${authUser}:${authPass}`).toString('base64');
  return `Basic ${token}`;
};

async function handler(request: NextRequest) {
  const path = request.nextUrl.pathname.replace('/api/backend', '');
  const url = `${backendBase}${path}${request.nextUrl.search}`;

  const init: RequestInit = {
    method: request.method,
    headers: {
      Authorization: buildAuthHeader(),
      'Content-Type': request.headers.get('content-type') || 'application/json',
    },
    cache: 'no-store',
  };

  if (request.method !== 'GET' && request.method !== 'HEAD') {
    init.body = await request.text();
  }

  const response = await fetch(url, init);
  const text = await response.text();
  return new NextResponse(text, {
    status: response.status,
    headers: {
      'Content-Type': response.headers.get('content-type') || 'application/json',
    },
  });
}

export { handler as GET, handler as POST, handler as PUT, handler as PATCH };
