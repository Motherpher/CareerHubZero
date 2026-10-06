import { NextResponse } from 'next/server';

export async function GET() {
  const secretConfigured = Boolean(process.env.WISH_BANK_SHARED_SECRET);
  const storageConfigured = Boolean(process.env.BLOB_READ_WRITE_TOKEN);
  return NextResponse.json({
    service: 'careerhub-wish-bank',
    status: secretConfigured && storageConfigured ? 'ok' : 'degraded',
    authoritative: true,
    intake_ready: secretConfigured && storageConfigured,
    ledger_ready: secretConfigured && storageConfigured,
    github_mirror_configured: Boolean(process.env.WISH_BANK_GITHUB_TOKEN),
  }, { status: secretConfigured && storageConfigured ? 200 : 503 });
}
