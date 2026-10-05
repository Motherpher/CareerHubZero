'use client';

import { FormEvent, useState } from 'react';

const categories = [
  ['navigation', 'Navigation'],
  ['profile', 'Profile'],
  ['search', 'Search'],
  ['geography', 'Geography'],
  ['analyse', 'Analyse'],
  ['apply', 'Apply'],
  ['track', 'Track'],
  ['library', 'Library'],
  ['accessibility', 'Accessibility'],
  ['visual', 'Visual / interaction design'],
  ['performance', 'Performance / reliability'],
  ['new_capability', 'New capability'],
  ['other', 'Other']
];

export default function WishForm({ language = 'en' }: { language?: string }) {
  const swedish = language.toLowerCase().startsWith('sv');
  const [state, setState] = useState<'idle' | 'sending' | 'done' | 'error'>('idle');
  const [message, setMessage] = useState('');

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState('sending');
    setMessage('');

    const form = new FormData(event.currentTarget);
    const response = await fetch('/api/wish', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        text: form.get('text'),
        category: form.get('category') || null,
        location_note: form.get('location_note') || null,
        route: window.location.pathname
      })
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      setState('error');
      setMessage(swedish ? 'Det gick inte att skicka önskemålet just nu.' : 'The wish could not be submitted right now.');
      return;
    }

    setState('done');
    setMessage(
      swedish
        ? `Tack. Önskemålet är skickat${data.wish_id ? ` (${data.wish_id})` : ''}.`
        : `Thank you. Your wish was submitted${data.wish_id ? ` (${data.wish_id})` : ''}.`
    );
    event.currentTarget.reset();
  }

  return (
    <form className="wish-form" onSubmit={submit}>
      <label>
        <span>{swedish ? 'Vad vill du ska bli enklare, tydligare eller möjligt?' : 'What would you like to be easier, clearer or possible?'}</span>
        <textarea name="text" required minLength={3} maxLength={4000} rows={7} />
      </label>

      <label>
        <span>{swedish ? 'Område (valfritt)' : 'Area (optional)'}</span>
        <select name="category" defaultValue="">
          <option value="">{swedish ? 'Välj om du vill' : 'Choose if useful'}</option>
          {categories.map(([value, label]) => <option value={value} key={value}>{label}</option>)}
        </select>
      </label>

      <label>
        <span>{swedish ? 'Var uppstod behovet? (valfritt)' : 'Where did this come up? (optional)'}</span>
        <input name="location_note" maxLength={300} />
      </label>

      <p className="wish-privacy">
        {swedish
          ? 'Skriv inte in känsliga personuppgifter eller innehåll från dokument om det inte är nödvändigt för att beskriva problemet.'
          : 'Do not paste sensitive personal data or document content unless it is necessary to explain the product issue.'}
      </p>

      <button type="submit" disabled={state === 'sending'}>
        {state === 'sending' ? (swedish ? 'Skickar…' : 'Sending…') : (swedish ? 'Skicka önskemål' : 'Submit wish')}
      </button>

      {message ? <p role="status" className={`wish-status wish-status--${state}`}>{message}</p> : null}
    </form>
  );
}
