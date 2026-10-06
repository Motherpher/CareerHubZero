import { notFound } from 'next/navigation';
import { loadHubProfile, loadPortfolioProfile, loadProfileShell } from '@/lib/profile';
import {
  loadPortfolioArchive,
  portfolioSectionSlug,
  portfolioWorkYear,
  worksForPortfolioSection,
} from '@/lib/portfolio';

type WriterAreaPageProps = {
  params: Promise<{ area: string }>;
};

export default async function WriterAreaPage({ params }: WriterAreaPageProps) {
  const { area } = await params;
  const hub = loadHubProfile();
  const shell = loadProfileShell();
  const portfolio = loadPortfolioProfile();
  const room = shell?.rooms?.find((candidate) => candidate.kind === 'portfolio');

  if (!shell?.enabled || !room || !portfolio) notFound();

  const sections = portfolio.sections ?? [];
  const archive = loadPortfolioArchive(portfolio);
  const showAll = area === 'all';
  const section = showAll
    ? null
    : sections.find((candidate, index) => portfolioSectionSlug(candidate, index) === area);

  if (!showAll && !section) notFound();

  const works = showAll ? archive : worksForPortfolioSection(archive, section!);
  const title = showAll ? 'All work' : section!.label;
  const description = showAll
    ? portfolio.archive?.note ?? 'The reconstructed portfolio archive.'
    : section!.description ?? 'Work in this portfolio area.';

  return (
    <main className={`workspace portfolio-room hub--${hub.experience.mode} hub--${hub.experience.density}`}>
      <header className="portfolio-masthead">
        <a className="breadcrumb" href="/writer">← Portfolio</a>
        <nav aria-label="Portfolio" className="nav nav--profile">
          <a href="/writer">Portfolio</a>
          {shell.rooms
            .filter((candidate) => candidate.kind === 'career')
            .map((candidate) => <a href={candidate.href} key={candidate.id}>{candidate.label}</a>)}
        </nav>

        <div className="portfolio-title-block">
          <p className="eyebrow">{showAll ? 'Archive' : 'Portfolio area'}</p>
          <h1>{title}</h1>
          <p className="lead">{description}</p>
        </div>
      </header>

      <section className="portfolio-links" aria-labelledby="area-work-title">
        <div>
          <p className="meta-label">{works.length} {works.length === 1 ? 'work' : 'works'}</p>
          <h2 id="area-work-title">{showAll ? 'Reconstructed archive' : `All ${title.toLocaleLowerCase()} work`}</h2>
        </div>
        <div className="portfolio-link-list">
          {works.length ? works.map((work, index) => {
            const metadata = [work.outlet, portfolioWorkYear(work), work.type].filter(Boolean).join(' · ');
            const body = (
              <>
                <span>{String(index + 1).padStart(2, '0')}</span>
                <span>
                  <strong>{work.title}</strong><br />
                  {metadata ? <><small>{metadata}</small><br /></> : null}
                  {work.note ? <small>{work.note}</small> : null}
                </span>
                <span aria-hidden="true">{work.url ? '↗' : ''}</span>
              </>
            );

            return work.url ? (
              <a href={work.url} key={work.id} target="_blank" rel="noreferrer">{body}</a>
            ) : (
              <div className="portfolio-work-row" key={work.id}>{body}</div>
            );
          }) : (
            <div className="portfolio-work-row">
              <span>—</span>
              <span>
                <strong>No archive entries are assigned to this area yet.</strong><br />
                <small>The area route exists, but its portfolio filter currently returns no verified works.</small>
              </span>
              <span />
            </div>
          )}
        </div>
      </section>

      <section className="portfolio-boundary" aria-label="Explore portfolio areas">
        <p className="meta-label">Explore</p>
        <h2>Move through the full body of work.</h2>
        <p>{portfolio.boundary?.text ?? 'The public portfolio is selective; the archive preserves the broader body of work.'}</p>
        <p>
          {sections.map((candidate, index) => (
            <span key={candidate.label}>
              <a className="text-link" href={`/writer/${portfolioSectionSlug(candidate, index)}`}>{candidate.label}</a>
              {' · '}
            </span>
          ))}
          <a className="text-link" href="/writer/all">All work</a>
        </p>
        <a className="text-link" href="/writer">Back to portfolio overview</a>
      </section>
    </main>
  );
}
