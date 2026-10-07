import type { Metadata } from 'next';
import type { CSSProperties, ReactNode } from 'react';
import GlobalProcessTray from '@/app/_components/GlobalProcessTray';
import { cssVars, loadHubProfile, loadProfileShell, loadTheme } from '@/lib/profile';
import './globals.css';
import './visual-language.css';
import './actions.css';
import './profile-shell.css';
import './motor.css';
import '../personal/profile.css';

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
  const language = hub.identity.language ?? 'en';
  const swedish = language.toLowerCase().startsWith('sv');
  const profileShell = Boolean(shell?.enabled);
  const improveLabel = profileShell
    ? (swedish ? 'Förbättra min profil' : 'Improve my profile')
    : (swedish ? 'Förbättra min CareerHub' : 'Improve my CareerHub');
  const bodyClass = [
    'experience',
    `experience--${hub.experience.mode}`,
    `density--${hub.experience.density}`,
    `motion--${hub.experience.motion ?? 'subtle'}`,
    `surface--${theme.surface.treatment}`,
    `imagery--${theme.imagery?.mode ?? 'none'}`
  ].join(' ');

  return (
    <html lang={language}>
      <body style={style} className={bodyClass}>
        <div className="visual-field" aria-hidden="true">
          <span className="visual-field__map" />
          <span className="visual-field__thread" />
          <span className="visual-field__leaf visual-field__leaf--one" />
          <span className="visual-field__leaf visual-field__leaf--two" />
          <span className="visual-field__sun" />
          <span className="visual-field__petal visual-field__petal--one" />
          <span className="visual-field__petal visual-field__petal--two" />
          <span className="visual-field__petal visual-field__petal--three" />
        </div>
        {children}
        <GlobalProcessTray language={language} />
        <a className="wish-launcher" href="/wish" aria-label={improveLabel}>{improveLabel}</a>
      </body>
    </html>
  );
}
