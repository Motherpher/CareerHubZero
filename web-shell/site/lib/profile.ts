import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';

export type ProfileRoomLink = {
  label: string;
  href: string;
};

export type ProfileRoom = {
  id: string;
  kind: 'portfolio' | 'career' | 'workspace';
  label: string;
  eyebrow?: string;
  description: string;
  href: string;
  cta?: string;
  features?: string[];
  links?: ProfileRoomLink[];
};

export type ProfileShell = {
  schema_version: '1.0';
  enabled: boolean;
  headline: string;
  intro?: string;
  rooms: ProfileRoom[];
};

export type HubProfile = {
  schema_version: '1.0';
  identity: {
    display_name: string;
    strapline?: string;
    language?: string;
    pronouns?: string;
    avatar_path?: string | null;
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
  modules?: {
    portfolio?: boolean;
    analytics?: boolean;
    profile_health?: boolean;
    geography?: boolean;
    hrdm_explainer?: boolean;
  };
  visibility?: {
    show_verified_sources?: boolean;
    show_match_scores?: boolean;
    show_hrdm_trace?: boolean;
    show_application_history?: boolean;
  };
};

export type ThemeTokens = {
  schema_version: '1.0';
  typography: {
    display: string;
    body: string;
    scale: 'compact' | 'standard' | 'large';
  };
  shape: {
    radius: 'square' | 'soft' | 'round';
    border?: 'none' | 'quiet' | 'defined';
  };
  surface: {
    treatment: 'flat' | 'layered' | 'editorial' | 'glass-light';
    shadow?: 'none' | 'subtle' | 'medium';
  };
  palette?: {
    background?: string;
    foreground?: string;
    muted?: string;
    accent?: string;
    accent_foreground?: string;
    secondary?: string;
    secondary_foreground?: string;
    highlight?: string;
    highlight_foreground?: string;
    signal?: string;
    signal_foreground?: string;
  };
  imagery?: {
    mode?: 'none' | 'portrait' | 'documentary' | 'graphic' | 'mixed';
    treatment?: 'natural' | 'monochrome' | 'muted' | 'high-contrast';
  };
};

const repoRoot = path.resolve(process.cwd(), '..');
const personalisationRoot = path.join(repoRoot, 'personalisation');

function readYaml<T>(fileName: string): T {
  const file = path.join(personalisationRoot, fileName);
  return YAML.parse(fs.readFileSync(file, 'utf8')) as T;
}

function readYamlOptional<T>(fileName: string): T | null {
  const file = path.join(personalisationRoot, fileName);
  if (!fs.existsSync(file)) return null;
  return YAML.parse(fs.readFileSync(file, 'utf8')) as T;
}

function readJson<T>(fileName: string): T {
  const file = path.join(personalisationRoot, fileName);
  return JSON.parse(fs.readFileSync(file, 'utf8')) as T;
}

export function loadHubProfile(): HubProfile {
  return readYaml<HubProfile>('hub.profile.yaml');
}

export function loadProfileShell(): ProfileShell | null {
  return readYamlOptional<ProfileShell>('profile.shell.yaml');
}

export function loadTheme(): ThemeTokens {
  return readJson<ThemeTokens>('theme.tokens.json');
}

function radiusValue(radius: ThemeTokens['shape']['radius']): string {
  if (radius === 'square') return '0px';
  if (radius === 'round') return '999px';
  return '8px';
}

function shadowValue(shadow: ThemeTokens['surface']['shadow']): string {
  if (shadow === 'medium') return '0 18px 48px rgba(24, 24, 24, 0.16)';
  if (shadow === 'subtle') return '0 8px 24px rgba(24, 24, 24, 0.08)';
  return 'none';
}

export function cssVars(theme: ThemeTokens): Record<string, string> {
  const p = theme.palette ?? {};
  const background = p.background ?? '#F6F5F2';
  const foreground = p.foreground ?? '#181818';
  const muted = p.muted ?? '#6B6B68';
  const accent = p.accent ?? '#2357D8';
  const accentForeground = p.accent_foreground ?? '#FFFFFF';
  const secondary = p.secondary ?? muted;
  const secondaryForeground = p.secondary_foreground ?? foreground;
  const highlight = p.highlight ?? accent;
  const highlightForeground = p.highlight_foreground ?? foreground;
  const signal = p.signal ?? accent;
  const signalForeground = p.signal_foreground ?? '#FFFFFF';

  return {
    '--ch-bg': background,
    '--ch-fg': foreground,
    '--ch-muted': muted,
    '--ch-accent': accent,
    '--ch-accent-fg': accentForeground,
    '--ch-secondary': secondary,
    '--ch-secondary-fg': secondaryForeground,
    '--ch-highlight': highlight,
    '--ch-highlight-fg': highlightForeground,
    '--ch-signal': signal,
    '--ch-signal-fg': signalForeground,
    '--ch-surface': 'var(--ch-bg)',
    '--ch-surface-alt': 'color-mix(in srgb, var(--ch-bg) 90%, var(--ch-fg) 10%)',
    '--ch-border': 'color-mix(in srgb, var(--ch-fg) 22%, transparent)',
    '--ch-accent-soft': 'color-mix(in srgb, var(--ch-accent) 16%, var(--ch-bg))',
    '--ch-secondary-soft': 'color-mix(in srgb, var(--ch-secondary) 24%, var(--ch-bg))',
    '--ch-highlight-soft': 'color-mix(in srgb, var(--ch-highlight) 26%, var(--ch-bg))',
    '--ch-signal-soft': 'color-mix(in srgb, var(--ch-signal) 15%, var(--ch-bg))',
    '--ch-display-font': theme.typography.display,
    '--ch-body-font': theme.typography.body,
    '--ch-radius': radiusValue(theme.shape.radius),
    '--ch-shadow': shadowValue(theme.surface.shadow)
  };
}
