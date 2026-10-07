'use client';

import { useMemo, useState } from 'react';
import styles from './help.module.css';

type HelpEntry = {
  id: string;
  section: string;
  question: string;
  answer: string;
  keywords: string[];
};

type Copy = {
  searchLabel: string;
  searchPlaceholder: string;
  noResults: string;
  clear: string;
  sections: Record<string, string>;
  entries: HelpEntry[];
};

const COPY: Record<'en' | 'sv', Copy> = {
  en: {
    searchLabel: 'Search help',
    searchPlaceholder: 'Search Profile, analysis, uploads, errors…',
    noResults: 'No help entry matched that search.',
    clear: 'Clear search',
    sections: {
      profile: 'Profile', search: 'Search', analyse: 'Job analysis', apply: 'Apply', track: 'Track',
      library: 'Library', status: 'Statuses & background work', sources: 'Sources & evidence', errors: 'Errors', privacy: 'Privacy & profile scope',
    },
    entries: [
      { id: 'profile-purpose', section: 'profile', question: 'What is my Profile?', answer: 'Your Profile is the verified professional context CareerHub may use across the career workspace. Review or rebuild it when career evidence changes. Search choices and temporary wishes do not become candidate evidence.', keywords: ['verified', 'career profile', 'evidence', 'rebuild', 'review'] },
      { id: 'profile-update', section: 'profile', question: 'How do I change professional information?', answer: 'Use the Profile workspace to add or update evidence, request a profile rebuild, or request review. CareerHub keeps the verified Profile separate from search-only preferences.', keywords: ['update', 'change', 'evidence', 'review', 'rebuild'] },

      { id: 'search-profile', section: 'search', question: 'What is the difference between my Search Profile and the filters on Search?', answer: 'The Search Profile is your saved baseline for future searches. The filters on the Search page are your latest Search workspace choices. They can persist for convenience, but they do not silently rewrite your verified Profile or saved Search Profile.', keywords: ['filters', 'baseline', 'saved search', 'search profile', 'workspace'] },
      { id: 'search-new', section: 'search', question: 'What do NEW, SEEN and CHANGED mean?', answer: 'NEW means the vacancy was not present in the comparable previous successful run. SEEN means it was already present without a material change. CHANGED means the vacancy was already known but relevant source information changed.', keywords: ['new', 'seen', 'changed', 'delta', 'results'] },
      { id: 'search-zero', section: 'search', question: 'What does “0 new jobs” mean?', answer: 'It means the search completed successfully but found no new or changed vacancies for the comparable search choices. A source or execution failure is shown separately and must not be presented as “0 new jobs.”', keywords: ['zero', '0 new', 'source warning', 'failed search', 'no jobs'] },
      { id: 'search-dismiss', section: 'search', question: 'What happens when I dismiss a vacancy with ×?', answer: 'CareerHub stores that decision for the active profile and hides the vacancy from normal repeated searches. You can explicitly show dismissed roles and restore one later.', keywords: ['dismiss', 'hide', 'restore', 'x', 'vacancy'] },
      { id: 'search-dates', section: 'search', question: 'How do the published and deadline filters work?', answer: 'Published date and application deadline are independent filters. You can use quick published-date periods or custom dates. If no deadline end date is set, CareerHub applies a reasonable horizon to avoid obviously irrelevant far-future deadlines.', keywords: ['published', 'deadline', 'week', 'month', 'date'] },

      { id: 'analyse-start', section: 'analyse', question: 'What happens when I choose Analyse job?', answer: 'CareerHub starts a durable Job Analysis for that vacancy. You can leave the page while it runs. The process continues independently of the browser page and the completed report is available through its stable result page.', keywords: ['analyse', 'job analysis', 'vacancy', 'start', 'report'] },
      { id: 'analyse-time', section: 'analyse', question: 'How long does Job Analysis take?', answer: 'A normal analysis is presented as taking a few minutes, commonly around 2–5 minutes. The active-process area shows the current state and links back to the analysis.', keywords: ['2–5', 'minutes', 'background', 'running', 'time'] },
      { id: 'analyse-recent', section: 'analyse', question: 'Where do completed analyses go?', answer: 'Completed analyses surface on their stable result page and in Recent analyses. Completion is only shown after the durable result has been persisted and read back successfully.', keywords: ['recent analyses', 'completed', 'result', 'stable url', 'persisted'] },

      { id: 'apply-purpose', section: 'apply', question: 'What is the Apply workspace for?', answer: 'Apply is where CareerHub turns a selected vacancy and your verified professional context into application material you can review and download before using it externally.', keywords: ['application', 'download', 'material', 'letter', 'cv'] },
      { id: 'apply-evidence', section: 'apply', question: 'Can search wishes become claims in an application?', answer: 'No. Search-only wishes and temporary filters are not candidate evidence. Application claims must remain bounded by verified professional evidence and permitted active sources.', keywords: ['claims', 'search wishes', 'evidence', 'application'] },

      { id: 'track-purpose', section: 'track', question: 'What is Track for?', answer: 'Track keeps the application lifecycle visible: status, priority, next action and related follow-up. Updating Track changes application state, not your verified professional Profile.', keywords: ['status', 'priority', 'next action', 'application', 'follow-up'] },

      { id: 'library-purpose', section: 'library', question: 'What is the Library?', answer: 'The Library is the profile-scoped place for professional source documents that may support your CareerHub. Uploading a document does not automatically mean an analysis may use it.', keywords: ['library', 'document', 'upload', 'professional source'] },
      { id: 'library-active', section: 'library', question: 'When can Job Analysis use a Library document?', answer: 'A document must be successfully processed and marked ACTIVE before it may enter Job Analysis as evidence. Stored-only or inactive documents must not be claimed as analysis evidence.', keywords: ['active', 'indexed', 'analysis evidence', 'inactive', 'processed'] },
      { id: 'library-controls', section: 'library', question: 'What can I do with an uploaded document?', answer: 'The Library lets you open, activate, deactivate, reload or erase a document through the normal profile-scoped controls. The visible state tells you whether it is available for analysis use.', keywords: ['open', 'activate', 'deactivate', 'reload', 'erase'] },

      { id: 'status-process', section: 'status', question: 'What do running and completed process states mean?', answer: 'Running means CareerHub has a durable active process that has not reached a terminal result. Completed means the expected durable output has been persisted and verified. Failed means the process reached an error state instead.', keywords: ['running', 'completed', 'failed', 'process', 'status'] },
      { id: 'status-navigation', section: 'status', question: 'Can I navigate away while an analysis is running?', answer: 'Yes. Changing rooms or reloading the page does not cancel the central analysis process. The global process area links back to running or completed work.', keywords: ['navigate', 'reload', 'background', 'global process'] },

      { id: 'sources-verified', section: 'sources', question: 'Which information can CareerHub treat as professional evidence?', answer: 'CareerHub distinguishes verified professional evidence from search-only preferences and temporary operating state. Only permitted professional sources may support candidate facts or application claims.', keywords: ['verified', 'sources', 'candidate facts', 'evidence', 'claims'] },
      { id: 'sources-library', section: 'sources', question: 'Does every uploaded file become evidence?', answer: 'No. A Library source must complete processing and be ACTIVE before it is eligible for analysis use. CareerHub should not describe an inactive or failed source as evidence used in an analysis.', keywords: ['upload', 'active', 'failed', 'source', 'evidence'] },

      { id: 'errors-search', section: 'errors', question: 'What should I do if Search shows a source warning?', answer: 'A source warning means CareerHub could not treat the run as a normal healthy search. It is different from a successful search with no new results. Retry later or adjust the search only if the message indicates your choices are the issue.', keywords: ['source warning', 'search error', 'retry', 'failed'] },
      { id: 'errors-analysis', section: 'errors', question: 'What if Job Analysis fails?', answer: 'A failed analysis remains distinct from a completed report. Use the process/result page to see the failure state and start a new analysis when the underlying issue is resolved.', keywords: ['analysis failed', 'error', 'result page', 'retry'] },
      { id: 'errors-library', section: 'errors', question: 'What if a Library document cannot be processed?', answer: 'A processing failure must remain visible and the document must not be treated as ACTIVE analysis evidence. Reload or replace the source when appropriate.', keywords: ['ingest failed', 'processing', 'library error', 'reload'] },

      { id: 'privacy-profile', section: 'privacy', question: 'Is Library and process data shared between CareerHub profiles?', answer: 'Normal CareerHub APIs scope Library objects, search decisions and process state to the active profile. A profile must not list, open or erase another profile’s normal workspace objects.', keywords: ['privacy', 'profile scoped', 'cross-profile', 'library', 'process'] },
      { id: 'privacy-binding', section: 'privacy', question: 'How does CareerHub know which profile is active?', answer: 'Production CareerHub resolves the profile manifest and its declared repository binding. A missing or mismatched production binding is treated as an error rather than silently switching profiles.', keywords: ['binding', 'repository', 'profile', 'production', 'mismatch'] },
    ],
  },
  sv: {
    searchLabel: 'Sök i hjälp',
    searchPlaceholder: 'Sök profil, analys, uppladdning, fel…',
    noResults: 'Ingen hjälppost matchade sökningen.',
    clear: 'Rensa sökning',
    sections: {
      profile: 'Profil', search: 'Sök', analyse: 'Jobbanalys', apply: 'Ansökan', track: 'Följ upp',
      library: 'Bibliotek', status: 'Status & bakgrundsarbete', sources: 'Källor & evidens', errors: 'Fel', privacy: 'Integritet & profilavgränsning',
    },
    entries: [
      { id: 'profile-purpose', section: 'profile', question: 'Vad är min Profil?', answer: 'Profilen är den verifierade professionella kontext som CareerHub får använda i karriärarbetsytan. Granska eller bygg om den när karriärevidensen ändras. Sökval och tillfälliga önskemål blir inte kandidatinformation.', keywords: ['verifierad', 'karriärprofil', 'evidens', 'bygg om', 'granska'] },
      { id: 'profile-update', section: 'profile', question: 'Hur ändrar jag professionell information?', answer: 'Använd Profil för att lägga till eller uppdatera evidens, begära ombyggnad av profilen eller begära granskning. CareerHub håller den verifierade Profilen åtskild från rena sökpreferenser.', keywords: ['uppdatera', 'ändra', 'evidens', 'granska', 'bygg om'] },

      { id: 'search-profile', section: 'search', question: 'Vad är skillnaden mellan min Sökprofil och filtren i Sök?', answer: 'Sökprofilen är din sparade baslinje för framtida sökningar. Filtren på Sök-sidan är dina senaste val i sökarbetsytan. De kan sparas för bekvämlighet men skriver inte om din verifierade Profil eller sparade Sökprofil.', keywords: ['filter', 'baslinje', 'sparad sökning', 'sökprofil', 'arbetsyta'] },
      { id: 'search-new', section: 'search', question: 'Vad betyder NEW, SEEN och CHANGED?', answer: 'NEW betyder att annonsen inte fanns i föregående jämförbara lyckade körning. SEEN betyder att den redan fanns utan materiell förändring. CHANGED betyder att den var känd men att relevant källinformation har ändrats.', keywords: ['new', 'seen', 'changed', 'delta', 'resultat'] },
      { id: 'search-zero', section: 'search', question: 'Vad betyder “0 nya jobb”?', answer: 'Det betyder att sökningen genomfördes korrekt men inte hittade några nya eller ändrade annonser för de jämförbara sökvalen. Källfel eller exekveringsfel visas separat och ska inte presenteras som “0 nya jobb”.', keywords: ['noll', '0 nya', 'källvarning', 'sökfel', 'inga jobb'] },
      { id: 'search-dismiss', section: 'search', question: 'Vad händer när jag väljer bort ett jobb med ×?', answer: 'CareerHub sparar beslutet för den aktiva profilen och döljer annonsen i normala upprepade sökningar. Du kan visa bortvalda jobb och återställa ett jobb senare.', keywords: ['välj bort', 'dölj', 'återställ', 'x', 'annons'] },
      { id: 'search-dates', section: 'search', question: 'Hur fungerar filter för publiceringsdatum och sista ansökningsdag?', answer: 'Publiceringsdatum och sista ansökningsdag är separata filter. Du kan använda snabba perioder eller egna datum. Om inget slutdatum för sista ansökningsdag anges använder CareerHub en rimlig horisont för att undvika uppenbart irrelevanta datum långt fram.', keywords: ['publicerad', 'sista ansökningsdag', 'vecka', 'månad', 'datum'] },

      { id: 'analyse-start', section: 'analyse', question: 'Vad händer när jag väljer Analysera jobbet?', answer: 'CareerHub startar en varaktig Jobbanalys för annonsen. Du kan lämna sidan medan den körs. Processen fortsätter oberoende av webbsidan och den färdiga rapporten finns på en stabil resultatsida.', keywords: ['analysera', 'jobbanalys', 'annons', 'starta', 'rapport'] },
      { id: 'analyse-time', section: 'analyse', question: 'Hur lång tid tar en Jobbanalys?', answer: 'En normal analys presenteras som att den tar några minuter, ofta omkring 2–5 minuter. Området för aktiva processer visar aktuell status och länkar tillbaka till analysen.', keywords: ['2–5', 'minuter', 'bakgrund', 'pågår', 'tid'] },
      { id: 'analyse-recent', section: 'analyse', question: 'Var hamnar färdiga analyser?', answer: 'Färdiga analyser visas på sin stabila resultatsida och under Senaste analyser. Analysen visas som färdig först när det varaktiga resultatet har sparats och kunnat läsas tillbaka.', keywords: ['senaste analyser', 'färdig', 'resultat', 'stabil sida', 'sparad'] },

      { id: 'apply-purpose', section: 'apply', question: 'Vad används Ansökan till?', answer: 'Ansökan är arbetsytan där CareerHub använder ett valt jobb och din verifierade professionella kontext för att skapa ansökningsmaterial som du kan granska och ladda ned innan du använder det externt.', keywords: ['ansökan', 'ladda ned', 'material', 'brev', 'cv'] },
      { id: 'apply-evidence', section: 'apply', question: 'Kan sököskemål bli påståenden i en ansökan?', answer: 'Nej. Sökönskemål och tillfälliga filter är inte kandidatinformation. Påståenden i ansökningsmaterial måste vara förankrade i verifierad professionell evidens och tillåtna aktiva källor.', keywords: ['påståenden', 'sökönskemål', 'evidens', 'ansökan'] },

      { id: 'track-purpose', section: 'track', question: 'Vad används Följ upp till?', answer: 'Följ upp håller ansökningsprocessen synlig: status, prioritet, nästa åtgärd och uppföljning. Ändringar här ändrar ansökningsstatus, inte din verifierade professionella Profil.', keywords: ['status', 'prioritet', 'nästa åtgärd', 'ansökan', 'uppföljning'] },

      { id: 'library-purpose', section: 'library', question: 'Vad är Biblioteket?', answer: 'Biblioteket är den profilavgränsade platsen för professionella källdokument som kan stödja CareerHub. Att ladda upp ett dokument innebär inte automatiskt att en analys får använda det.', keywords: ['bibliotek', 'dokument', 'ladda upp', 'professionell källa'] },
      { id: 'library-active', section: 'library', question: 'När kan Jobbanalys använda ett dokument i Biblioteket?', answer: 'Dokumentet måste ha behandlats utan fel och vara markerat ACTIVE innan det får ingå som evidens i Jobbanalys. Dokument som bara lagras eller är inaktiva får inte beskrivas som använd analys-evidens.', keywords: ['active', 'indexerad', 'analys evidens', 'inaktiv', 'behandlad'] },
      { id: 'library-controls', section: 'library', question: 'Vad kan jag göra med ett uppladdat dokument?', answer: 'I Biblioteket kan du öppna, aktivera, inaktivera, läsa in på nytt eller radera ett dokument via de normala profilavgränsade kontrollerna. Den synliga statusen visar om dokumentet är tillgängligt för analys.', keywords: ['öppna', 'aktivera', 'inaktivera', 'läs in', 'radera'] },

      { id: 'status-process', section: 'status', question: 'Vad betyder pågående och färdig process?', answer: 'Pågående betyder att CareerHub har en varaktig aktiv process som ännu inte nått ett slutresultat. Färdig betyder att det förväntade varaktiga resultatet har sparats och verifierats. Misslyckad betyder att processen avslutades med ett fel.', keywords: ['pågår', 'färdig', 'misslyckad', 'process', 'status'] },
      { id: 'status-navigation', section: 'status', question: 'Kan jag lämna sidan medan en analys körs?', answer: 'Ja. Att byta arbetsyta eller ladda om sidan avbryter inte den centrala analysprocessen. Det globala processområdet länkar tillbaka till pågående eller färdigt arbete.', keywords: ['navigera', 'ladda om', 'bakgrund', 'global process'] },

      { id: 'sources-verified', section: 'sources', question: 'Vilken information får CareerHub behandla som professionell evidens?', answer: 'CareerHub skiljer verifierad professionell evidens från sökpreferenser och tillfälligt arbetsläge. Endast tillåtna professionella källor får stödja kandidatfakta eller påståenden i ansökningar.', keywords: ['verifierad', 'källor', 'kandidatfakta', 'evidens', 'påståenden'] },
      { id: 'sources-library', section: 'sources', question: 'Blir varje uppladdad fil automatiskt evidens?', answer: 'Nej. En Bibliotekskälla måste vara färdigbehandlad och ACTIVE innan den kan användas i analys. CareerHub ska inte beskriva en inaktiv eller misslyckad källa som använd evidens.', keywords: ['uppladdning', 'active', 'misslyckad', 'källa', 'evidens'] },

      { id: 'errors-search', section: 'errors', question: 'Vad gör jag om Sök visar en källvarning?', answer: 'En källvarning betyder att CareerHub inte kunde behandla körningen som en normal frisk sökning. Det skiljer sig från en lyckad sökning utan nya resultat. Försök igen senare eller ändra sökval endast om meddelandet visar att valen är problemet.', keywords: ['källvarning', 'sökfel', 'försök igen', 'misslyckad'] },
      { id: 'errors-analysis', section: 'errors', question: 'Vad händer om Jobbanalys misslyckas?', answer: 'En misslyckad analys hålls åtskild från en färdig rapport. Använd process- eller resultatsidan för att se felstatus och starta en ny analys när grundproblemet är löst.', keywords: ['analys misslyckad', 'fel', 'resultatsida', 'försök igen'] },
      { id: 'errors-library', section: 'errors', question: 'Vad händer om ett dokument i Biblioteket inte kan behandlas?', answer: 'Ett behandlingsfel ska förbli synligt och dokumentet får inte behandlas som ACTIVE analys-evidens. Läs in källan på nytt eller ersätt den när det är lämpligt.', keywords: ['behandlingsfel', 'bibliotek fel', 'läs in', 'källa'] },

      { id: 'privacy-profile', section: 'privacy', question: 'Delas Bibliotek och processdata mellan olika CareerHub-profiler?', answer: 'Normala CareerHub-API:er avgränsar Biblioteksobjekt, sökbeslut och processstatus till den aktiva profilen. En profil ska inte kunna lista, öppna eller radera en annan profils normala arbetsyteobjekt.', keywords: ['integritet', 'profilavgränsad', 'mellan profiler', 'bibliotek', 'process'] },
      { id: 'privacy-binding', section: 'privacy', question: 'Hur vet CareerHub vilken profil som är aktiv?', answer: 'I produktion löser CareerHub profilmanifestet och dess deklarerade repository-bindning. En saknad eller felaktig produktionsbindning behandlas som ett fel i stället för att tyst byta profil.', keywords: ['bindning', 'repository', 'profil', 'produktion', 'felmatchning'] },
    ],
  },
};

export default function HelpClient({ language = 'en' }: { language?: string }) {
  const locale: 'en' | 'sv' = language.toLowerCase().startsWith('sv') ? 'sv' : 'en';
  const copy = COPY[locale];
  const [query, setQuery] = useState('');
  const normalized = query.trim().toLowerCase();

  const entries = useMemo(() => {
    if (!normalized) return copy.entries;
    return copy.entries.filter((entry) => [entry.question, entry.answer, copy.sections[entry.section], ...entry.keywords].join(' ').toLowerCase().includes(normalized));
  }, [copy, normalized]);

  const sections = Object.keys(copy.sections).filter((section) => entries.some((entry) => entry.section === section));

  return (
    <div className={styles.help}>
      <div className={styles.searchBox}>
        <label htmlFor="help-search">{copy.searchLabel}</label>
        <div className={styles.searchRow}>
          <input id="help-search" type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder={copy.searchPlaceholder} autoComplete="off" />
          {query ? <button type="button" onClick={() => setQuery('')}>{copy.clear}</button> : null}
        </div>
      </div>

      {entries.length === 0 ? <p className={styles.empty}>{copy.noResults}</p> : null}

      {sections.map((section) => (
        <section className={styles.section} id={section} key={section}>
          <h2>{copy.sections[section]}</h2>
          <div className={styles.entries}>
            {entries.filter((entry) => entry.section === section).map((entry) => (
              <details className={styles.entry} id={entry.id} key={entry.id} open={Boolean(normalized)}>
                <summary>{entry.question}</summary>
                <p>{entry.answer}</p>
              </details>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
