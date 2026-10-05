import fs from 'node:fs';
import path from 'node:path';
import { NextResponse } from 'next/server';

const artifactRoot = path.resolve(process.cwd(), '.careerhub-artifacts');
const ALLOWED_ROOTS = ['output/', 'reports/'];

function safeArtifact(relativePath: string) {
  const normalized = relativePath.replaceAll('\\', '/').replace(/^\/+/, '');
  if (!ALLOWED_ROOTS.some((prefix) => normalized.startsWith(prefix))) return null;
  const full = path.resolve(artifactRoot, normalized);
  if (!full.startsWith(artifactRoot + path.sep) || !fs.existsSync(full) || !fs.statSync(full).isFile()) return null;
  return { full, normalized };
}

export async function GET(request: Request) {
  const url = new URL(request.url);
  const requested = url.searchParams.get('path') || '';
  const artifact = safeArtifact(requested);
  if (!artifact) return NextResponse.json({ error: 'Artifact not found.' }, { status: 404 });
  const buffer = fs.readFileSync(artifact.full);
  const ext = path.extname(artifact.full).toLowerCase();
  const contentType = ext === '.json' ? 'application/json' : ext === '.docx' ? 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' : ext === '.md' ? 'text/markdown; charset=utf-8' : 'application/octet-stream';
  return new Response(new Uint8Array(buffer), {
    headers: {
      'content-type': contentType,
      'content-disposition': `attachment; filename="${path.basename(artifact.full).replaceAll('"', '')}"`,
      'cache-control': 'private, no-store',
    },
  });
}
