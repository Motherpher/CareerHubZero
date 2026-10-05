import WishForm from './WishForm';
import { loadHubProfile } from '@/lib/profile';

export default function WishPage() {
  const hub = loadHubProfile();
  const swedish = (hub.identity.language ?? 'en').toLowerCase().startsWith('sv');

  return (
    <main className="wish-page">
      <a href="/" className="wish-back">← {swedish ? 'Tillbaka' : 'Back'}</a>
      <p className="eyebrow">CareerHub Wish Bank</p>
      <h1>{swedish ? 'Förbättra min CareerHub' : 'Improve my CareerHub'}</h1>
      <p className="lead">
        {swedish
          ? 'Berätta vad som skulle göra din CareerHub enklare, tydligare eller mer användbar. Önskemålet går till den gemensamma utvecklingsbanken och kan bli underlag för kommande utvecklingsarbete.'
          : 'Tell us what would make your CareerHub easier, clearer or more useful. Your wish goes into the shared development bank and can become input to future development work.'}
      </p>
      <WishForm language={hub.identity.language ?? 'en'} />
    </main>
  );
}
