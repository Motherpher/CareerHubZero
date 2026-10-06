import type { Metadata } from 'next';
import type { CSSProperties, ReactNode } from 'react';
import { cssVars, loadHubProfile, loadProfileShell, loadTheme } from '@/lib/profile';
import './globals.css';
import './actions.css';
import './profile-shell.css';
import './motor.css';

export function generateMetadata(): Metadata {
  const hub = loadHubProfile();
  const shell = loadProfileShell();
  const title = shell?.enabled ? `${hub.identity.display_name} · Profile` : `${hub.identity.display_name} · CareerHub`;
  return { title, description: hub.identity.strapline ?? 'Personal professional workspace' };
}

export default function RootLayout({ children }: { children: ReactNode }) {
  const hub = loadHubProfile();
  const shell = loadProfileShell();
  const theme = loadTheme();
  const style = cssVars(theme) as CSSProperties;
  const swedish = (hub.identity.language ?? 'en').toLowerCase().startsWith('sv');
  const profileShell = Boolean(shell?.enabled);
  const improveLabel = profileShell
    ? (swedish ? 'Förbättra min profil' : 'Improve my profile')
    : (swedish ? 'Förbättra min CareerHub' : 'Improve my CareerHub');

  return (
    <html lang={hub.identity.language ?? 'en'}>
      <body style={style}>
        {children}
        <a className="wish-launcher" href="/wish" aria-label={improveLabel}>{improveLabel}</a>
      </body>
    </html>
  );
}
