import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ service: 'careerhub-wish-bank', status: 'ok' });
}
