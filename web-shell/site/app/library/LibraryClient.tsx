'use client';

import { FormEvent, useCallback, useEffect, useState } from 'react';

type LibraryFile = {
  pathname: string;
  display_name: string;
  active: boolean;
  status: string;
  document_class: string;
  uploaded_at: string;
  size: number;
};

const DOCUMENT_CLASSES = [
  ['cv', 'CV'],
  ['certificate', 'Certificate'],
  ['diploma', 'Diploma'],
  ['employment_certificate', 'Employment certificate'],
  ['role_description', 'Role description'],
  ['work_sample', 'Work sample'],
  ['portfolio', 'Portfolio'],
  ['project_description', 'Project description'],
  ['reference', 'Reference'],
  ['course_record', 'Course record'],
  ['prior_application', 'Prior application'],
  ['other', 'Other'],
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
    event.preventDefault();
    setBusy(true); setMessage('');
    const form = new FormData(event.currentTarget);
    const response = await fetch('/api/library', { method: 'POST', body: form });
    const data = await response.json().catch(() => ({}));
    setMessage(response.ok ? `Document uploaded as ${data.document_class ?? 'source'} and ${data.active ? 'activated' : 'stored inactive'}.` : (data.error ?? 'Upload failed.'));
    if (response.ok) { event.currentTarget.reset(); await refreshFiles(); }
    setBusy(false);
  }

  async function manage(file: LibraryFile, action: 'activate' | 'deactivate' | 'erase') {
    if (action === 'erase' && !window.confirm(`Erase ${file.display_name} from your private CareerHub library?`)) return;
    setBusy(true); setMessage('');
    const response = await fetch('/api/library', { method: 'PATCH', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ pathname: file.pathname, action }) });
    const data = await response.json().catch(() => ({}));
    const success = action === 'erase' ? 'Source erased.' : action === 'activate' ? 'Source activated.' : 'Source deactivated.';
    setMessage(response.ok ? success : (data.error ?? 'Update failed.'));
    if (response.ok) await refreshFiles();
    setBusy(false);
  }

  async function requestReview(file: LibraryFile) {
    setBusy(true); setMessage('');
    const response = await fetch('/api/action', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ operation: 'library_review', payload: { pathname: file.pathname, filename: file.display_name, document_class: file.document_class, active: file.active } }),
    });
    const data = await response.json().catch(() => ({}));
    setMessage(response.ok ? `${data.message ?? 'Evidence review requested.'}${data.action_id ? ` Reference: ${data.action_id}` : ''}` : (data.error ?? data.message ?? 'Review request failed.'));
    setBusy(false);
  }

  async function rebuildIndex() {
    setBusy(true); setMessage('');
    const response = await fetch('/api/library/reload', { method: 'POST' });
    const data = await response.json().catch(() => ({}));
    setMessage(response.ok ? (data.message ?? 'CareerHub library reloaded.') : (data.error ?? 'Library reload failed.'));
    setBusy(false);
  }

  return (
    <div className="section-stack">
      <form className="action-form" onSubmit={upload}>
        <div className="action-form__grid">
          <label className="field field--full"><span>Add a career source</span><input type="file" name="file" required accept=".pdf,.doc,.docx,.txt,.md,.rtf,.odt,.png,.jpg,.jpeg" /></label>
          <label className="field"><span>Document class</span><select name="document_class" defaultValue="cv">{DOCUMENT_CLASSES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
          <label className="field"><span>Initial state</span><select name="initial_state" defaultValue="active"><option value="active">ACTIVE — available to CareerHub</option><option value="inactive">INACTIVE — store only</option></select></label>
        </div>
        <p className="wish-privacy">Server upload currently supports files up to about 4.3 MB. Uploading does not automatically rewrite the active Career Profile.</p>
        <button className="button button--primary" disabled={busy} type="submit">{busy ? 'Working…' : 'Upload document'}</button>
      </form>
      <div className="inline-actions"><button className="button button--primary" type="button" disabled={busy} onClick={() => void rebuildIndex()}>Reload CareerHub Library</button><a className="button" href="/profile">Review active profile</a></div>
      {message ? <p role="status" className="wish-status">{message}</p> : null}
      <div className="section-stack">{files.length ? files.map((file) => <div className="row row--stack-mobile" key={file.pathname}><div><strong>{file.display_name}</strong><div className="muted">{file.status} · {file.document_class.replaceAll('_',' ')} · {Math.max(1, Math.round(file.size / 1024))} KB</div></div><div className="inline-actions"><a className="button" href={`/api/library/file?pathname=${encodeURIComponent(file.pathname)}`} target="_blank" rel="noreferrer">Open</a><button className="button" type="button" disabled={busy} onClick={() => void manage(file, file.active ? 'deactivate' : 'activate')}>{file.active ? 'Deactivate' : 'Activate'}</button><button className="button" type="button" disabled={busy} onClick={() => void requestReview(file)}>Request evidence review</button><button className="button" type="button" disabled={busy} onClick={() => void manage(file, 'erase')}>Erase</button></div></div>) : <div className="empty-state">No uploaded library sources yet.</div>}</div>
    </div>
  );
}
