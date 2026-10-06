import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';

export type ProfileRoomLink = {
  label: string;
  href: string;
};

export type ProfileRoom = {
  id: string;
  label: string;
  eyebrow?: string;
  description: string;
  href: string;
  cta?: string;
  features?: string[];
  links?: ProfileRoomLink[];
};

export type HubProfile = {
  schema_version: '1.0';
  identity: {
    display_name: string;
    strapline?: string;
    language?: string;
  };
  experience: {
    mode: 'editorial' | 'analytical' | 'guided' | 'portfolio' | 'compact' | 'custom';
    density: 'airy' | 'balanced' | 'dense';
    guidance: 'minimal' | 'standard' | 'high';
    motion?: 'reduced' | 'subtle' | 'expressive';
  };
  home: {
    headline?: string;
    intro?: string;
    slots: string[];
  };
  navigation: {
    primary: string[];
    labels?: Record<string, string>;
  };
  profile_shell?: {
    enabled?: boolean;
    headline?: string;
    intro?: string;
    rooms?: ProfileRoom[];
  };
};

export type ThemeTokens = {
  schema_version: '1.0';
  typography?: { display?: string; body?: string; scale?: string };
  shape?: { radius?: string; border?: string };
  surface?: { treatment?: string; shadow?: string };
  palette?: Record<string, string>;
};

const repoRoot = path.resolve(process.cwd(), '..');
const personalisationRoot = path.join(repoRoot, 'personalisation');

function readYaml<T>(fileName: string): T {
  const file = path.join(personalisationRoot, fileName);
  return YAML.parse(fs.readFileSync(file, 'utf8')) as T;
}

function readJson<T>(fileName: string): T {
  const file = path.join(personalisationRoot, fileName);
  return JSON.parse(fs.readFileSync(file, 'utf8')) as T;
}

export function loadHubProfile(): HubProfile {
  return readYaml<HubProfile>('hub.profile.yaml');
}

export function loadTheme(): ThemeTokens {
  return readJson<ThemeTokens>('theme.tokens.json');
}

export function cssVars(theme: ThemeTokens): Record<string, string> {
  const p = theme.palette ?? {};
  return {
    '--ch-bg': p.background ?? '#F6F5F2',
    '--ch-fg': p.foreground ?? '#181818',
    '--ch-muted': p.muted ?? '#6B6B68',
    '--ch-accent': p.accent ?? '#2357D8',
    '--ch-accent-fg': p.accent_foreground ?? '#FFFFFF',
    '--ch-surface': p.surface ?? p.background ?? '#F6F5F2',
    '--ch-surface-alt': p.surface_alt ?? '#ECEAE4',
    '--ch-border': p.border ?? '#C9C5BC',
    '--ch-accent-soft': p.accent_soft ?? '#E6ECFA',
    '--ch-display-font': theme.typography?.display ?? 'ui-sans-serif, system-ui, sans-serif',
    '--ch-body-font': theme.typography?.body ?? 'ui-sans-serif, system-ui, sans-serif',
    '--ch-radius': theme.shape?.radius ?? '8px',
    '--ch-shadow': theme.surface?.shadow ?? 'none'
  };
}
