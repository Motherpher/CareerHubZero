import type { Metadata } from 'next';
import type { CSSProperties, ReactNode } from 'react';
import { cssVars, loadHubProfile, loadTheme } from '@/lib/profile';
import './globals.css';
import './actions.css';
import './motor.css';

export function generateMetadata(): Metadata {
  const hub = loadHubProfile();
  return { title: `${hub.identity.display_name} · CareerHub`, description: hub.identity.strapline ?? 'Personal CareerHub' };
}

export default function RootLayout({ children }: { children: ReactNode }) {
  const hub = loadHubProfile();
  const theme = loadTheme();
  const style = cssVars(theme) as CSSProperties;
  const swedish = (hub.identity.language ?? 'en').toLowerCase().startsWith('sv');
  return (
    <html lang={hub.identity.language ?? 'en'}>
      <body style={style}>
        {children}
        <a className="wish-launcher" href="/wish" aria-label={swedish ? 'Förbättra min CareerHub' : 'Improve my CareerHub'}>{swedish ? 'Förbättra min CareerHub' : 'Improve my CareerHub'}</a>
      </body>
    </html>
  );
}
