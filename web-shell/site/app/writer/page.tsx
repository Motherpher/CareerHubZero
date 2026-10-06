import { notFound } from 'next/navigation';
import {
  loadHubProfile,
  loadPortfolioProfile,
  loadProfileShell,
  type PortfolioSection,
} from '@/lib/profile';
import {
  loadPortfolioArchive,
  portfolioSectionSlug,
  worksForPortfolioSection,
} from '@/lib/portfolio';

export default function WriterPortfolioPage() {
  const hub = loadHubProfile();
  const shell = loadProfileShell();
  const portfolio = loadPortfolioProfile();
  const room = shell?.rooms?.find((candidate) => candidate.kind === 'portfolio');

  if (!shell?.enabled || !room) notFound();

  const sections: PortfolioSection[] = portfolio?.sections?.length
    ? portfolio.sections
    : (room.features ?? []).map((feature) => ({ label: feature, description: undefined }));
  const featured = portfolio?.featured ?? [];
  const archive = loadPortfolioArchive(portfolio);

  return (
    <main className={`workspace portfolio-room hub--${hub.experience.mode} hub--${hub.experience.density}`}>
      <header className="portfolio-masthead">
        <a className="breadcrumb" href="/">← {shell.headline ?? hub.identity.display_name}</a>
        <nav aria-label="Portfolio" className="nav nav--profile">
          <a href="/writer" aria-current="page">Portfolio</a>
          {shell.rooms
            .filter((candidate) => candidate.kind === 'career')
            .map((candidate) => <a href={candidate.href} key={candidate.id}>{candidate.label}</a>)}
        </nav>

        <div className="portfolio-title-block">
          <p className="eyebrow">{portfolio?.eyebrow ?? room.eyebrow ?? 'Portfolio'}</p>
          <h1>{room.label}</h1>
          <p className="lead">{portfolio?.intro ?? room.description}</p>
        </div>
      </header>

      <section className="portfolio-intro" aria-labelledby="portfolio-intro-title">
        <div>
          <p className="meta-label">Selected practice</p>
          <h2 id="portfolio-intro-title">{portfolio?.headline ?? 'Writing, reporting and editorial work.'}</h2>
        </div>
        <p className="portfolio-intro__copy">{portfolio?.intro ?? room.description}</p>
      </section>

      {sections.length ? (
        <section className="portfolio-departments" aria-label="Portfolio areas">
          {sections.map((section, index) => {
            const slug = portfolioSectionSlug(section, index);
            const count = archive.length ? worksForPortfolioSection(archive, section).length : null;
            return (
              <a
                className={`portfolio-department${index === 0 ? ' portfolio-department--lead' : ''}`}
                href={`/writer/${slug}`}
                key={section.label}
                style={{ color: 'inherit', textDecoration: 'none' }}
                aria-label={`Open ${section.label}`}
              >
                <span>{String(index + 1).padStart(2, '0')}</span>
                <p className="meta-label">Area</p>
                <h2>{section.label}</h2>
                <p className="portfolio-department__action">
                  {count === null ? 'Open area →' : `View ${count} ${count === 1 ? 'work' : 'works'} →`}
                </p>
                {section.description ? <p>{section.description}</p> : null}
              </a>
            );
          })}
        </section>
      ) : null}

      {featured.length ? (
        <section className="portfolio-links" aria-labelledby="featured-work-title">
          <div>
            <p className="meta-label">Selected work</p>
            <h2 id="featured-work-title">Featured reporting & writing</h2>
          </div>
          <div className="portfolio-link-list">
            {featured.map((item, index) => (
              item.href ? (
                <a href={item.href} key={`${item.title}-${index}`} target="_blank" rel="noreferrer">
                  <span>{String(index + 1).padStart(2, '0')}</span>
                  <span>
                    <strong>{item.title}</strong><br />
                    <small>{[item.outlet, item.year, item.type].filter(Boolean).join(' · ')}</small><br />
                    <small>{item.description}</small>
                  </span>
                  <span aria-hidden="true">↗</span>
                </a>
              ) : (
                <div className="portfolio-work-row" key={`${item.title}-${index}`}>
                  <span>{String(index + 1).padStart(2, '0')}</span>
                  <span>
                    <strong>{item.title}</strong><br />
                    <small>{[item.outlet, item.year, item.type].filter(Boolean).join(' · ')}</small><br />
                    <small>{item.description}</small>
                  </span>
                  <span />
                </div>
              )
            ))}
          </div>
        </section>
      ) : null}

      <section className="portfolio-boundary" aria-label="Portfolio archive">
        <p className="meta-label">Archive</p>
        <h2>
          {archive.length
            ? `${archive.length} ${portfolio?.archive?.label ?? 'works in the reconstructed archive'}`
            : portfolio?.archive?.count
              ? `${portfolio.archive.count} ${portfolio.archive.label ?? 'works in the reconstructed archive'}`
              : portfolio?.boundary?.title ?? 'Public portfolio'}
        </h2>
        <p>{portfolio?.archive?.note ?? portfolio?.boundary?.text ?? 'This is the site-facing portfolio view.'}</p>
        {portfolio?.boundary?.text && portfolio?.archive?.note ? <p>{portfolio.boundary.text}</p> : null}
        {archive.length ? (
          <a className="text-link" href="/writer/all">Browse all {archive.length} works →</a>
        ) : (
          <a className="text-link" href="/">Back to profile home</a>
        )}
      </section>
    </main>
  );
}
