export type SearchFilters = {
  jobTypes: string[];
  workModes: Array<'onsite' | 'hybrid' | 'remote'>;
  publishedFrom: string;
  publishedTo: string;
  deadlineFrom: string;
  deadlineTo: string;
  publishedPresetDays: number | null;
};

export type SearchWorkspaceState = {
  schema_version: '1.0';
  profile_id: string;
  updated_at: string;
  filters: SearchFilters;
};

export type DismissedJob = {
  identityKey: string;
  title: string;
  company: string;
  url: string;
  dismissed_at: string;
};

export type DismissalState = {
  schema_version: '1.0';
  profile_id: string;
  updated_at: string;
  jobs: DismissedJob[];
};

export const EMPTY_FILTERS: SearchFilters = {
  jobTypes: [],
  workModes: [],
  publishedFrom: '',
  publishedTo: '',
  deadlineFrom: '',
  deadlineTo: '',
  publishedPresetDays: null,
};

export function normalizeFilters(raw: unknown): SearchFilters {
  const input = raw && typeof raw === 'object' ? raw as Record<string, unknown> : {};
  const strings = (value: unknown) => Array.isArray(value) ? value.map(String).map((item) => item.trim()).filter(Boolean).slice(0, 12) : [];
  const workModes = strings(input.workModes).filter((value): value is 'onsite' | 'hybrid' | 'remote' => ['onsite', 'hybrid', 'remote'].includes(value));
  const preset = Number(input.publishedPresetDays);
  return {
    jobTypes: strings(input.jobTypes),
    workModes,
    publishedFrom: typeof input.publishedFrom === 'string' ? input.publishedFrom.slice(0, 10) : '',
    publishedTo: typeof input.publishedTo === 'string' ? input.publishedTo.slice(0, 10) : '',
    deadlineFrom: typeof input.deadlineFrom === 'string' ? input.deadlineFrom.slice(0, 10) : '',
    deadlineTo: typeof input.deadlineTo === 'string' ? input.deadlineTo.slice(0, 10) : '',
    publishedPresetDays: [7, 30, 60, 90].includes(preset) ? preset : null,
  };
}

export function effectivePublishedFrom(filters: SearchFilters, now = new Date()): string {
  if (filters.publishedPresetDays) {
    const date = new Date(now);
    date.setUTCDate(date.getUTCDate() - filters.publishedPresetDays);
    return date.toISOString().slice(0, 10);
  }
  return filters.publishedFrom;
}

export function effectiveDeadlineTo(filters: SearchFilters, now = new Date()): string {
  if (filters.deadlineTo) return filters.deadlineTo;
  const horizon = new Date(now);
  horizon.setUTCDate(horizon.getUTCDate() + 180);
  return horizon.toISOString().slice(0, 10);
}

export function inferWorkMode(location: string, description: string): 'onsite' | 'hybrid' | 'remote' {
  const text = `${location} ${description}`.toLowerCase();
  if (/\b(remote|distans|hemifrån|home[- ]?office|remote-first)\b/i.test(text)) return 'remote';
  if (/\b(hybrid|hybridarbete|hybrid work|delvis distans)\b/i.test(text)) return 'hybrid';
  return 'onsite';
}

export function matchesFilters(job: {
  published: string;
  deadline: string;
  jobType: string;
  workMode: string;
}, filters: SearchFilters, now = new Date()): boolean {
  const published = job.published.slice(0, 10);
  const deadline = job.deadline.slice(0, 10);
  const from = effectivePublishedFrom(filters, now);
  const deadlineTo = effectiveDeadlineTo(filters, now);
  if (from && published && published < from) return false;
  if (filters.publishedTo && published && published > filters.publishedTo) return false;
  if (filters.deadlineFrom && deadline && deadline < filters.deadlineFrom) return false;
  if (deadlineTo && deadline && deadline > deadlineTo) return false;
  if (filters.jobTypes.length && !filters.jobTypes.some((type) => job.jobType.toLowerCase().includes(type.toLowerCase()))) return false;
  if (filters.workModes.length && !filters.workModes.includes(job.workMode as 'onsite' | 'hybrid' | 'remote')) return false;
  return true;
}

export function searchStatePath(profileId: string): string {
  return `search-state/${encodeURIComponent(profileId)}/workspace.json`;
}

export function dismissalStatePath(profileId: string): string {
  return `search-state/${encodeURIComponent(profileId)}/dismissed.json`;
}
