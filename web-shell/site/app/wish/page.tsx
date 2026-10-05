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
          ? 'Skriv vad som skulle göra din CareerHub enklare, tydligare eller mer användbar för dig. Vi sorterar önskemålet så att sådant som gäller just din profil kan utvecklas där, medan förbättringar som hör hemma i CareerHub-motorn kan komma alla CareerHubs till del.'
          : 'Tell us what would make your CareerHub easier, clearer or more useful for you. We sort the wish so profile-specific improvements stay with your hub, while motor-level improvements can benefit every CareerHub.'}
      </p>
      <WishForm language={hub.identity.language ?? 'en'} />
    </main>
  );
}
