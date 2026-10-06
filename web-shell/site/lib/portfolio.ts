import fs from 'node:fs';
import path from 'node:path';
import type { PortfolioProfile, PortfolioSection } from './profile';

export type PortfolioWork = {
  id: string;
  date?: string;
  title: string;
  outlet?: string;
  language?: string;
  type?: string;
  evidence?: string;
  status?: string;
  url?: string;
  themes?: string[];
  phase?: string;
  featured?: boolean;
  note?: string;
};

type PortfolioCorpus = {
  works?: PortfolioWork[];
};

const siteRoot = process.cwd();
const instanceRoot = path.resolve(siteRoot, '..');
const repositoryRoot = path.resolve(instanceRoot, '..');
const personalisationRoot = path.join(instanceRoot, 'personalisation');

function normalized(value: string | undefined): string {
  return (value ?? '').trim().toLocaleLowerCase();
}

function includesAny(haystack: string, needles: string[] | undefined): boolean {
  if (!needles?.length) return false;
  return needles.some((needle) => haystack.includes(normalized(needle)));
}

export function portfolioSectionSlug(section: PortfolioSection, index = 0): string {
  if (section.slug?.trim()) return section.slug.trim();
  const slug = section.label
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
  return slug || `area-${index + 1}`;
}

export function loadPortfolioArchive(portfolio: PortfolioProfile | null): PortfolioWork[] {
  const source = portfolio?.archive?.source?.trim();
  if (!source || !source.endsWith('.json')) return [];

  const sourcePath = path.resolve(personalisationRoot, source);
  const insideRepository = sourcePath.startsWith(`${repositoryRoot}${path.sep}`);
  if (!insideRepository || !fs.existsSync(sourcePath)) return [];

  try {
    const parsed = JSON.parse(fs.readFileSync(sourcePath, 'utf8')) as PortfolioCorpus;
    return (parsed.works ?? [])
      .filter((work) => work?.id && work?.title)
      .filter((work) => !work.status || normalized(work.status) === 'verified')
      .sort((a, b) => normalized(b.date).localeCompare(normalized(a.date)));
  } catch {
    return [];
  }
}

export function workMatchesPortfolioSection(work: PortfolioWork, section: PortfolioSection): boolean {
  const filter = section.filter;
  if (!filter) return true;

  const workId = normalized(work.id);
  const phase = normalized(work.phase);
  const type = normalized(work.type);
  const themes = (work.themes ?? []).map(normalized);
  const text = normalized([
    work.id,
    work.title,
    work.outlet,
    work.type,
    work.phase,
    work.note,
    ...(work.themes ?? []),
  ].filter(Boolean).join(' '));

  const checks: boolean[] = [];

  if (filter.ids?.length) {
    checks.push(filter.ids.map(normalized).includes(workId));
  }
  if (filter.phases?.length) {
    checks.push(filter.phases.map(normalized).includes(phase));
  }
  if (filter.type_contains?.length) {
    checks.push(includesAny(type, filter.type_contains));
  }
  if (filter.themes?.length) {
    const wanted = filter.themes.map(normalized);
    checks.push(themes.some((theme) => wanted.includes(theme)));
  }
  if (filter.text_contains?.length) {
    checks.push(includesAny(text, filter.text_contains));
  }

  return checks.length ? checks.some(Boolean) : true;
}

export function worksForPortfolioSection(works: PortfolioWork[], section: PortfolioSection): PortfolioWork[] {
  return works.filter((work) => workMatchesPortfolioSection(work, section));
}

export function portfolioWorkYear(work: PortfolioWork): string | undefined {
  const match = work.date?.match(/^\d{4}/);
  return match?.[0];
}
