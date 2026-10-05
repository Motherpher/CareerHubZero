import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';

export type CareerHubManifest = {
  schema_version: string;
  profile_id: string;
  ui?: { language?: string };
};

const repoRoot = path.resolve(process.cwd(), '..');

export function loadCareerHubManifest(): CareerHubManifest {
  const file = path.join(repoRoot, 'careerhub.yaml');
  return YAML.parse(fs.readFileSync(file, 'utf8')) as CareerHubManifest;
}
