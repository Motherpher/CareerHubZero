import { Buffer } from 'node:buffer';
import { createHash } from 'node:crypto';
import { del, get, list, put } from '@vercel/blob';
import mammoth from 'mammoth';
import { PDFParse } from 'pdf-parse';
import type { RuntimeProfileContext } from '@/lib/profile-context';
import { assertProfileOwnedPath } from '@/lib/profile-context';

export type LibrarySourceStatus =
  | 'UPLOADED'
  | 'INGESTING'
  | 'INDEXED'
  | 'ACTIVE'
  | 'INACTIVE'
  | 'INGEST_FAILED'
  | 'ERASED';

export type LibrarySource = {
  schema_version: '2.0';
  source_id: string;
  profile_id: string;
  filename: string;
  content_type: string;
  document_class: string;
  status: LibrarySourceStatus;
  requested_active: boolean;
  uploaded_at: string;
  updated_at: string;
  hash: string;
  size: number;
  storage: { provider: 'vercel_blob'; pathname: string; access: 'private' };
  extraction: {
    state: 'PENDING' | 'COMPLETE' | 'FAILED';
    extracted_text_ref: string | null;
    completed_at: string | null;
    char_count: number;
    error: string | null;
  };
};

export type EvidenceUseSource = {
  source_id: string;
  filename: string;
  document_class: string;
  hash: string;
  status: 'ACTIVE';
  extracted_text_ref: string;
  char_count: number;
  excerpt: string;
  truncated: boolean;
};

function now() { return new Date().toISOString(); }
function safeName(name: string) { return name.replace(/[^a-zA-Z0-9._-]+/g, '-').replace(/-+/g, '-').slice(0, 140) || 'document'; }
function sourceRoot(context: RuntimeProfileContext, sourceId: string) { return `${context.libraryPrefix}sources/${sourceId}/`; }
export function sourceMetadataPath(context: RuntimeProfileContext, sourceId: string) { return `${sourceRoot(context, sourceId)}source.json`; }
export function sourceExtractedPath(context: RuntimeProfileContext, sourceId: string) { return `${sourceRoot(context, sourceId)}extracted.txt`; }
export function sourceRawPath(context: RuntimeProfileContext, sourceId: string, filename: string) { return `${sourceRoot(context, sourceId)}raw/${safeName(filename)}`; }

export async function readPrivateText(pathname: string): Promise<string | null> {
  try {
    const result = await get(pathname, { access: 'private' });
    if (!result || result.statusCode !== 200) return null;
    return await new Response(result.stream).text();
  } catch { return null; }
}

export async function readPrivateJson<T = any>(pathname: string): Promise<T | null> {
  const text = await readPrivateText(pathname);
  if (!text) return null;
  try { return JSON.parse(text) as T; } catch { return null; }
}

export async function writeSourceMetadata(context: RuntimeProfileContext, source: LibrarySource) {
  const path = sourceMetadataPath(context, source.source_id);
  assertProfileOwnedPath(path, context.libraryPrefix);
  await put(path, JSON.stringify(source, null, 2), {
    access: 'private', addRandomSuffix: false, allowOverwrite: true, contentType: 'application/json',
  });
}

export async function extractDocumentText(filename: string, contentType: string, bytes: Buffer): Promise<string> {
  const lower = filename.toLowerCase();
  if (contentType.startsWith('text/') || /\.(txt|md|csv|json|yaml|yml)$/i.test(lower)) {
    return bytes.toString('utf8').replace(/\u0000/g, '').trim();
  }
  if (/\.rtf$/i.test(lower) || contentType === 'application/rtf') {
    return bytes.toString('utf8').replace(/\\'[0-9a-f]{2}/gi, ' ').replace(/\\[a-z]+\d* ?/gi, ' ').replace(/[{}]/g, ' ').replace(/\s+/g, ' ').trim();
  }
  if (/\.docx$/i.test(lower) || contentType.includes('wordprocessingml')) {
    const result = await mammoth.extractRawText({ buffer: bytes });
    return result.value.trim();
  }
  if (/\.pdf$/i.test(lower) || contentType === 'application/pdf') {
    const parser = new PDFParse({ data: bytes });
    try {
      const result = await parser.getText();
      return String(result.text || '').trim();
    } finally { await parser.destroy(); }
  }
  throw new Error('This document type cannot be text-indexed yet.');
}

export async function ingestUpload(
  context: RuntimeProfileContext,
  sourceId: string,
  file: File,
  documentClass: string,
  requestedActive: boolean,
): Promise<LibrarySource> {
  const bytes = Buffer.from(await file.arrayBuffer());
  const rawPath = sourceRawPath(context, sourceId, file.name);
  assertProfileOwnedPath(rawPath, context.libraryPrefix);
  const timestamp = now();
  const source: LibrarySource = {
    schema_version: '2.0', source_id: sourceId, profile_id: context.profileId,
    filename: file.name, content_type: file.type || 'application/octet-stream', document_class: documentClass,
    status: 'UPLOADED', requested_active: requestedActive, uploaded_at: timestamp, updated_at: timestamp,
    hash: `sha256:${createHash('sha256').update(bytes).digest('hex')}`, size: bytes.length,
    storage: { provider: 'vercel_blob', pathname: rawPath, access: 'private' },
    extraction: { state: 'PENDING', extracted_text_ref: null, completed_at: null, char_count: 0, error: null },
  };
  await put(rawPath, bytes, { access: 'private', addRandomSuffix: false, contentType: source.content_type });
  await writeSourceMetadata(context, source);

  source.status = 'INGESTING'; source.updated_at = now(); await writeSourceMetadata(context, source);
  try {
    const text = await extractDocumentText(file.name, source.content_type, bytes);
    if (!text) throw new Error('No usable text could be extracted from the document.');
    const extractedPath = sourceExtractedPath(context, sourceId);
    await put(extractedPath, text, { access: 'private', addRandomSuffix: false, allowOverwrite: true, contentType: 'text/plain; charset=utf-8' });
    source.extraction = { state: 'COMPLETE', extracted_text_ref: extractedPath, completed_at: now(), char_count: text.length, error: null };
    source.status = 'INDEXED'; source.updated_at = now(); await writeSourceMetadata(context, source);
    source.status = requestedActive ? 'ACTIVE' : 'INACTIVE'; source.updated_at = now(); await writeSourceMetadata(context, source);
  } catch (error) {
    source.status = 'INGEST_FAILED';
    source.updated_at = now();
    source.extraction = { ...source.extraction, state: 'FAILED', completed_at: now(), error: error instanceof Error ? error.message : 'Document ingestion failed.' };
    await writeSourceMetadata(context, source);
  }
  return source;
}

export async function listLibrarySources(context: RuntimeProfileContext): Promise<LibrarySource[]> {
  const result = await list({ prefix: `${context.libraryPrefix}sources/` });
  const metadataPaths = result.blobs.map(b => b.pathname).filter(p => p.endsWith('/source.json'));
  const sources = (await Promise.all(metadataPaths.map(path => readPrivateJson<LibrarySource>(path)))).filter(Boolean) as LibrarySource[];
  return sources.filter(source => source.profile_id === context.profileId && source.status !== 'ERASED').sort((a,b) => b.uploaded_at.localeCompare(a.uploaded_at));
}

export async function setSourceStatus(context: RuntimeProfileContext, sourceId: string, action: 'activate' | 'deactivate'): Promise<LibrarySource> {
  const source = await readPrivateJson<LibrarySource>(sourceMetadataPath(context, sourceId));
  if (!source || source.profile_id !== context.profileId) throw new Error('Library source not found in active profile.');
  if (action === 'activate') {
    if (source.extraction.state !== 'COMPLETE' || !source.extraction.extracted_text_ref) throw new Error('Source cannot be activated before successful ingestion.');
    source.status = 'ACTIVE';
  } else source.status = 'INACTIVE';
  source.updated_at = now();
  await writeSourceMetadata(context, source);
  return source;
}

export async function eraseSource(context: RuntimeProfileContext, sourceId: string): Promise<void> {
  const metaPath = sourceMetadataPath(context, sourceId);
  const source = await readPrivateJson<LibrarySource>(metaPath);
  if (!source || source.profile_id !== context.profileId) throw new Error('Library source not found in active profile.');
  const objects = await list({ prefix: sourceRoot(context, sourceId) });
  if (objects.blobs.length) await del(objects.blobs.map(blob => blob.url));
  const tombstone = { schema_version: '1.0', source_id: sourceId, profile_id: context.profileId, hash: source.hash, filename: source.filename, status: 'ERASED', erased_at: now() };
  const tombstonePath = `${context.libraryPrefix}tombstones/${sourceId}.json`;
  await put(tombstonePath, JSON.stringify(tombstone, null, 2), { access: 'private', addRandomSuffix: false, allowOverwrite: true, contentType: 'application/json' });
}

export async function buildActiveEvidenceContext(context: RuntimeProfileContext, maxSources = 8, maxCharsPerSource = 6000, maxTotalChars = 40000) {
  const sources = (await listLibrarySources(context)).filter(source => source.status === 'ACTIVE' && source.extraction.state === 'COMPLETE' && source.extraction.extracted_text_ref);
  const used: EvidenceUseSource[] = [];
  let remaining = maxTotalChars;
  for (const source of sources.slice(0, maxSources)) {
    if (remaining <= 0) break;
    const text = await readPrivateText(source.extraction.extracted_text_ref!);
    if (!text) continue;
    const take = Math.min(maxCharsPerSource, remaining);
    const excerpt = text.slice(0, take);
    used.push({ source_id: source.source_id, filename: source.filename, document_class: source.document_class, hash: source.hash, status: 'ACTIVE', extracted_text_ref: source.extraction.extracted_text_ref!, char_count: source.extraction.char_count, excerpt, truncated: excerpt.length < text.length });
    remaining -= excerpt.length;
  }
  return {
    schema_version: '1.0', profile_id: context.profileId, built_at: now(), source_count: used.length,
    sources: used,
    source_ids: used.map(source => source.source_id),
    source_hashes: used.map(source => source.hash),
  };
}
