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
  const anchors = search?.geographies?.anchors ?? [];
  const engagement = search?.engagement_types ?? [];
  const savedNeed = search?.user_search_overlay?.specific_wishes_or_needs ?? '';

  return (
    <main className="workspace">
      <WorkspaceHeader
        current="find"
        title={sv ? 'Sök' : 'Search'}
        intro={sv
          ? 'Sök från din verifierade karriärprofil. Om du vill kan du lägga till specifika önskemål eller behov för just den här sökningen.'
          : 'Search from your verified career profile. If you want, add specific wishes or needs for this search.'}
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
          <h2>{sv ? 'Sök jobb nu' : 'Run search now'}</h2>
          <SearchRunner language={language} />
        </article>

        <article className="panel panel--full">
          <h2>{sv ? 'Ändra sparade sökinställningar' : 'Edit saved Search Profile'}</h2>
          <SearchProfileEditor anchors={anchors} remoteAllowed={Boolean(search?.geographies?.remote_allowed)} engagementTypes={engagement} savedNeed={savedNeed} language={language} />
        </article>

        <article className="panel">
          <h2>{sv ? 'Geografisk breddning' : 'Geographical widening'}</h2>
          <ol>{(search?.geographies?.progressive_widening ?? []).map((item: string) => <li key={item}>{item.replaceAll('_', ' ')}</li>)}</ol>
        </article>

        <article className="panel">
          <h2>{sv ? 'För just den här sökningen' : 'For this search only'}</h2>
          <p className="muted">
            {sv
              ? 'Specifika önskemål eller behov fungerar endast som ett extra raster för den aktuella sökningen. De blir aldrig kandidatfakta och förändrar inte din verifierade karriärprofil.'
              : 'Specific wishes or needs act only as an extra raster for the current search. They never become candidate evidence or change your verified career profile.'}
          </p>
          <div className="inline-actions"><a className="button" href="/wish">{sv ? 'Föreslå en förbättring' : 'Suggest a search improvement'}</a></div>
        </article>
      </section>
    </main>
  );
}
