import SearchRunner from '@/app/find/SearchRunner';
import SearchProfileEditor from '@/app/find/SearchProfileEditor';
import WorkspaceHeader from '@/app/_components/WorkspaceHeader';
import { loadSearchProfile } from '@/lib/data';
import { loadHubProfile } from '@/lib/profile';

export default function SearchPage() {
  const search = loadSearchProfile();
  const hub = loadHubProfile();
  const language = hub.identity.language ?? 'en';
  const sv = language.toLowerCase().startsWith('sv');
  const lanes = search?.lanes ?? [];
  const anchors = search?.geographies?.anchors ?? [];
  const engagement = search?.engagement_types ?? [];
  const savedNeed = search?.user_search_overlay?.specific_wishes_or_needs ?? '';

  return (
    <main className="workspace">
      <WorkspaceHeader
        current="find"
        title={sv ? 'Sök' : 'Search'}
        intro={sv
          ? 'Sök från din verifierade karriärprofil. Du kan lägga till specifika önskemål eller behov för just den här sökningen utan att ändra profilen.'
          : 'Search from your verified career profile. You can add specific wishes or needs for this search without changing the profile.'}
      />
      <section className="panel-grid">
        <article className="panel panel--full">
          <p className="meta-label">{sv ? 'Sparad sökprofil' : 'Saved search profile'}</p>
          <h2>{anchors.join(' + ') || (sv ? 'Inga geografiska ankare angivna' : 'No geographic anchors configured')}</h2>
          <div className="tag-row">
            {search?.geographies?.remote_allowed ? <span className="tag">{sv ? 'Distans tillåten' : 'Remote allowed'}</span> : null}
            {engagement.map((item: string) => <span className="tag" key={item}>{item}</span>)}
          </div>
        </article>

        <article className="panel panel--full">
          <p className="meta-label">{sv ? 'Starta sökning' : 'Activate search'}</p>
          <h2>{sv ? 'Sök jobb nu' : 'Run the saved profile now'}</h2>
          <SearchRunner lanes={lanes} language={language} />
        </article>

        <article className="panel panel--full">
          <h2>{sv ? 'Ändra sparade sökinställningar' : 'Edit saved Search Profile'}</h2>
          <SearchProfileEditor anchors={anchors} remoteAllowed={Boolean(search?.geographies?.remote_allowed)} engagementTypes={engagement} savedNeed={savedNeed} language={language} />
        </article>

        <article className="panel panel--full">
          <h2>{sv ? 'Sökspår' : 'Role lanes'}</h2>
          <div className="section-stack">
            {lanes.map((lane: any) => <div className="row" key={lane.lane_id}><strong>{lane.name}</strong><span className="status">P{lane.priority} · {lane.bucket}</span></div>)}
          </div>
        </article>

        <article className="panel">
          <h2>{sv ? 'Geografisk breddning' : 'Geographical widening'}</h2>
          <ol>{(search?.geographies?.progressive_widening ?? []).map((item: string) => <li key={item}>{item.replaceAll('_', ' ')}</li>)}</ol>
        </article>

        <article className="panel">
          <h2>{sv ? 'För just den här sökningen' : 'This-search overrides'}</h2>
          <p className="muted">
            {sv
              ? 'Specifika önskemål eller behov i sökrutan fungerar endast som ett extra raster för den aktuella sökningen. De blir aldrig kandidatfakta.'
              : 'Specific wishes or needs in the search field act only as an extra raster for the current search. They never become candidate evidence.'}
          </p>
          <div className="inline-actions"><a className="button" href="/wish">{sv ? 'Föreslå en förbättring' : 'Suggest a search improvement'}</a></div>
        </article>
      </section>
    </main>
  );
}
