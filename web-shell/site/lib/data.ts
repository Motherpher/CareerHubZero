import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';
import { loadCareerHubManifest } from '@/lib/manifest';

const repoRoot = path.resolve(process.cwd(), '..');

function readText(relativePath: string): string | null {
  const file = path.join(repoRoot, relativePath);
  if (!fs.existsSync(file)) return null;
  return fs.readFileSync(file, 'utf8');
}

export function readYaml<T = any>(relativePath: string): T | null {
  const text = readText(relativePath);
  if (!text) return null;
  return YAML.parse(text) as T;
}

export function readJson<T = any>(relativePath: string): T | null {
  const text = readText(relativePath);
  if (!text) return null;
  return JSON.parse(text) as T;
}

export function loadCandidateProfile() {
  const manifest = loadCareerHubManifest();
  return readYaml<any>(manifest.profile?.path ?? 'profile/candidate_verified.yaml');
}

export function loadSearchProfile() {
  const manifest = loadCareerHubManifest();
  return readYaml<any>(manifest.search?.path ?? 'config/search_profile.yaml');
}

export function loadJobVault() {
  const manifest = loadCareerHubManifest();
  return readJson<any>(manifest.state?.job_vault ?? 'data/job_vault.json') ?? { jobs: [] };
}

export function loadApplications() {
  const manifest = loadCareerHubManifest();
  return readJson<any>(manifest.state?.applications ?? 'data/applications.json') ?? { applications: [] };
}

export function loadHrdmLedger() {
  const manifest = loadCareerHubManifest();
  return readJson<any>(manifest.state?.hrdm_ledger ?? 'data/hrdm_ledger.json') ?? { runs: [] };
}

export function candidateEvidenceCount() {
  const profile = loadCandidateProfile();
  return Array.isArray(profile?.evidence) ? profile.evidence.length : 0;
}

export function careerSourceCount() {
  const profile = loadCandidateProfile();
  return Array.isArray(profile?.career_sources) ? profile.career_sources.length : 0;
}
