'use client';

import { FormEvent, useCallback, useEffect, useState } from 'react';

type LibraryFile = {
  source_id: string;
  pathname: string;
  display_name: string;
  active: boolean;
  status: string;
  document_class: string;
  uploaded_at: string;
  updated_at: string;
  size: number;
  hash: string;
  ingestion: string;
  char_count: number;
  ingestion_error?: string | null;
};

const DOCUMENT_CLASSES = [
  ['cv', 'CV'], ['certificate', 'Certificate'], ['diploma', 'Diploma'],
  ['employment_certificate', 'Employment certificate'], ['role_description', 'Role description'],
  ['work_sample', 'Work sample'], ['portfolio', 'Portfolio'], ['project_description', 'Project description'],
  ['reference', 'Reference'], ['course_record', 'Course record'], ['prior_application', 'Prior application'], ['other', 'Other'],
];

export default function LibraryClient() {
  const [files, setFiles] = useState<LibraryFile[]>([]);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  const refreshFiles = useCallback(async () => {
    const response = await fetch('/api/library', { cache: 'no-store' });
    const data = await response.json().catch(() => ({}));
    setFiles(data.files ?? []);
    if (!response.ok && data.error) setMessage(data.error);
  }, []);
  useEffect(() => { void refreshFiles(); }, [refreshFiles]);

  async function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setMessage('Uploading and indexing document…');
    const form = new FormData(event.currentTarget);
    const response = await fetch('/api/library', { method: 'POST', body: form });
    const data = await response.json().catch(() => ({}));
    if (response.ok) {
      setMessage(data.active ? 'Document indexed and ACTIVE — it can now be used as source-bounded analysis evidence.' : 'Document indexed and stored INACTIVE — it will not be used in analysis until activated.');
      event.currentTarget.reset();
      await refreshFiles();
    } else {
      setMessage(data.error ?? 'Upload or ingestion failed. The document has not become active evidence.');
      await refreshFiles();
    }
    setBusy(false);
  }

  async function manage(file: LibraryFile, action: 'activate' | 'deactivate' | 'erase') {
    if (action === 'erase' && !window.confirm(`Erase ${file.display_name} from your private CareerHub library?`)) return;
    setBusy(true); setMessage('');
    const response = await fetch('/api/library', { method: 'PATCH', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ source_id: file.source_id, action }) });
    const data = await response.json().catch(() => ({}));
    const success = action === 'erase' ? 'Source erased and excluded from future evidence context.' : action === 'activate' ? 'Source ACTIVE — available to future Job Analysis.' : 'Source INACTIVE — excluded from future analysis.';
    setMessage(response.ok ? success : (data.error ?? 'Update failed.'));
    if (response.ok) await refreshFiles();
    setBusy(false);
  }

  async function rebuildIndex() {
    setBusy(true); setMessage('Rebuilding ACTIVE evidence index…');
    const response = await fetch('/api/library/reload', { method: 'POST' });
    const data = await response.json().catch(() => ({}));
    setMessage(response.ok ? (data.message ?? 'CareerHub Library evidence index rebuilt.') : (data.error ?? 'Library reload failed.'));
    setBusy(false);
  }

  return (
    <div className="section-stack">
      <form className="action-form" onSubmit={upload}>
        <div className="action-form__grid">
          <label className="field field--full"><span>Add a career source</span><input type="file" name="file" required accept=".pdf,.docx,.txt,.md,.rtf,.csv,.json,.yaml,.yml" /></label>
          <label className="field"><span>Document class</span><select name="document_class" defaultValue="cv">{DOCUMENT_CLASSES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
          <label className="field"><span>After successful indexing</span><select name="initial_state" defaultValue="active"><option value="active">ACTIVE — allow in Job Analysis</option><option value="inactive">INACTIVE — store/index only</option></select></label>
        </div>
        <p className="wish-privacy">Upload does not rewrite your verified Career Profile. A document becomes analysis evidence only after text extraction succeeds and its status is ACTIVE.</p>
        <button className="button button--primary" disabled={busy} type="submit">{busy ? 'Working…' : 'Upload and index document'}</button>
      </form>
      <div className="inline-actions"><button className="button button--primary" type="button" disabled={busy} onClick={() => void rebuildIndex()}>Rebuild ACTIVE evidence index</button><a className="button" href="/profile">Review verified profile</a></div>
      {message ? <p role="status" className="wish-status">{message}</p> : null}
      <div className="section-stack">{files.length ? files.map((file) => <div className="row row--stack-mobile" key={file.source_id}><div><strong>{file.display_name}</strong><div className="muted">{file.status} · ingestion {file.ingestion} · {file.document_class.replaceAll('_',' ')} · {Math.max(1, Math.round(file.size / 1024))} KB{file.char_count ? ` · ${file.char_count.toLocaleString()} chars indexed` : ''}</div>{file.ingestion_error ? <div className="notice notice--warning">{file.ingestion_error}</div> : null}<small className="muted">Source ID: {file.source_id} · {file.hash}</small></div><div className="inline-actions"><a className="button" href={`/api/library/file?pathname=${encodeURIComponent(file.pathname)}`} target="_blank" rel="noreferrer">Open</a><button className="button" type="button" disabled={busy || file.ingestion !== 'COMPLETE'} onClick={() => void manage(file, file.active ? 'deactivate' : 'activate')}>{file.active ? 'Deactivate' : 'Activate'}</button><button className="button" type="button" disabled={busy} onClick={() => void manage(file, 'erase')}>Erase</button></div></div>) : <div className="empty-state">No uploaded Library sources yet.</div>}</div>
    </div>
  );
}
