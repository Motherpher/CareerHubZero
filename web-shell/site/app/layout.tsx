import type { Metadata } from 'next';
import type { CSSProperties, ReactNode } from 'react';
import { cssVars, loadHubProfile, loadTheme } from '@/lib/profile';
import './globals.css';

export function generateMetadata(): Metadata {
  const hub = loadHubProfile();
  return {
    title: `${hub.identity.display_name} · CareerHub`,
    description: hub.identity.strapline ?? 'Personal CareerHub'
  };
}

export default function RootLayout({ children }: { children: ReactNode }) {
  const hub = loadHubProfile();
  const theme = loadTheme();
  const style = cssVars(theme) as CSSProperties;

  return (
    <html lang={hub.identity.language ?? 'en'}>
      <body style={style}>{children}</body>
    </html>
  );
}
