from __future__ import annotations

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import feedparser
import requests
from bs4 import BeautifulSoup

from .models import Job, clean_text

UA = "CareerHub/0.2.4 (+https://github.com/Motherpher/CareerHubZero)"
TIMEOUT = 15


class SourceError(RuntimeError):
    pass


def load_yaml(path):
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "sv,en,pl;q=0.8,*;q=0.5"})
    return s


def dedupe(jobs: list[Job]) -> list[Job]:
    seen = {}
    for job in jobs:
        title = re.sub(r"[^\wåäöé]+", " ", clean_text(job.title).lower()).strip()
        company = re.sub(r"[^\wåäöé]+", " ", clean_text(job.company).lower()).strip()
        location = re.sub(r"[^\wåäöé]+", " ", clean_text(job.location).lower()).strip()
        if title and company:
            key = f"{company}|{title}|{location}"
        else:
            key = (job.url or f"{company}|{title}|{location}").strip().lower()
        if key not in seen or len(clean_text(job.description)) > len(clean_text(seen[key].description)):
            seen[key] = job
    return list(seen.values())


def platsbanken(query: str, limit: int = 20) -> list[Job]:
    r = session().get(
        "https://jobsearch.api.jobtechdev.se/search",
        params={"q": query, "limit": min(limit, 100), "offset": 0},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    jobs = []
    for h in r.json().get("hits", []):
        employer = h.get("employer") or {}
        addr = h.get("workplace_address") or {}
        app = h.get("application_details") or {}
        desc = h.get("description") or {}
        title = h.get("headline") or (h.get("occupation") or {}).get("label") or ""
        company = employer.get("name") or employer.get("workplace") or ""
        location = ", ".join(x for x in [addr.get("municipality"), addr.get("region")] if x)
        url = h.get("webpage_url") or app.get("url") or ""
        if not url and h.get("id"):
            url = f"https://arbetsformedlingen.se/platsbanken/annonser/{h['id']}"
        employment = h.get("employment_type")
        work_model = h.get("workplace_model")
        jobs.append(Job(
            source="platsbanken",
            provider_id=str(h.get("id") or ""),
            title=title,
            company=company,
            location=location,
            employment_type=employment.get("label", "") if isinstance(employment, dict) else str(employment or ""),
            work_mode=work_model.get("label", "") if isinstance(work_model, dict) else str(work_model or ""),
            published=str(h.get("publication_date") or ""),
            deadline=str(h.get("last_publication_date") or ""),
            url=url,
            description=desc.get("text_formatted") or desc.get("text") or "",
            matched_query=query,
            provider_meta={"occupation": h.get("occupation"), "duration": h.get("duration")},
        ))
    return jobs


def remotive_all() -> list[Job]:
    r = session().get("https://remotive.com/api/remote-jobs", timeout=TIMEOUT)
    r.raise_for_status()
    return [
        Job(
            source="remotive",
            provider_id=str(h.get("id") or ""),
            title=h.get("title") or "",
            company=h.get("company_name") or "",
            location=h.get("candidate_required_location") or "Remote",
            employment_type=h.get("job_type") or "",
            work_mode="remote",
            published=h.get("publication_date") or "",
            url=h.get("url") or "",
            salary=h.get("salary") or "",
            description=h.get("description") or "",
            provider_meta={"category": h.get("category")},
        )
        for h in r.json().get("jobs", [])
    ]


def remoteok_all() -> list[Job]:
    r = session().get("https://remoteok.com/api", timeout=TIMEOUT)
    r.raise_for_status()
    jobs = []
    for h in r.json():
        if not isinstance(h, dict) or not (h.get("position") or h.get("id")):
            continue
        tags = h.get("tags") or []
        jobs.append(Job(
            source="remoteok",
            provider_id=str(h.get("id") or ""),
            title=h.get("position") or "",
            company=h.get("company") or "",
            location=h.get("location") or "Remote",
            work_mode="remote",
            published=str(h.get("date") or h.get("epoch") or ""),
            url=h.get("url") or h.get("apply_url") or "",
            salary=" - ".join(str(x) for x in [h.get("salary_min"), h.get("salary_max")] if x),
            description=" ".join([clean_text(h.get("description")), " ".join(tags)]),
            provider_meta={"tags": tags},
        ))
    return jobs


def wwr_all() -> list[Job]:
    r = session().get("https://weworkremotely.com/remote-jobs.rss", timeout=TIMEOUT)
    r.raise_for_status()
    feed = feedparser.loads(r.text)
    jobs = []
    for e in feed.entries:
        summary = e.get("summary") or e.get("description") or ""
        title = e.get("title") or ""
        company = ""
        if ":" in title:
            company, title = [x.strip() for x in title.split(":", 1)]
        jobs.append(Job(
            source="weworkremotely",
            provider_id=e.get("id") or e.get("guid") or "",
            title=title,
            company=company,
            location="Remote",
            work_mode="remote",
            published=e.get("published") or e.get("updated") or "",
            url=e.get("link") or "",
            description=summary,
        ))
    return jobs


def adzuna(query: str, location: str = "", country: str = "se", limit: int = 20) -> list[Job]:
    app_id, app_key = os.getenv("ADZUNA_APP_ID"), os.getenv("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        return []
    url = f"https://api.adzuna.com/v1/api/jobs/{country.lower()}/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": min(limit, 50),
        "what": query,
        "content-type": "application/json",
    }
    if location:
        params["where"] = location
    r = session().get(url, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    jobs = []
    for h in r.json().get("results", []):
        loc = h.get("location") or {}
        company = h.get("company") or {}
        jobs.append(Job(
            source="adzuna",
            provider_id=str(h.get("id") or ""),
            title=h.get("title") or "",
            company=company.get("display_name") or "",
            location=loc.get("display_name") or "",
            employment_type=("full_time" if h.get("full_time") else "part_time" if h.get("part_time") else ""),
            published=h.get("created") or "",
            url=h.get("redirect_url") or "",
            salary=" - ".join(str(x) for x in [h.get("salary_min"), h.get("salary_max")] if x),
            description=h.get("description") or "",
            matched_query=query,
        ))
    return jobs


def jooble(query: str, location: str = "", limit: int = 20) -> list[Job]:
    key, endpoint = os.getenv("JOOBLE_API_KEY"), os.getenv("JOOBLE_API_ENDPOINT")
    if not key or not endpoint:
        return []
    r = session().post(endpoint.rstrip("/") + "/" + key, json={"keywords": query, "location": location, "page": 1}, timeout=TIMEOUT)
    r.raise_for_status()
    jobs = []
    for h in (r.json().get("jobs") or [])[:limit]:
        jobs.append(Job(
            source="jooble",
            provider_id=str(h.get("id") or ""),
            title=h.get("title") or "",
            company=h.get("company") or "",
            location=h.get("location") or "",
            employment_type=h.get("type") or "",
            published=h.get("updated") or "",
            url=h.get("link") or "",
            salary=h.get("salary") or "",
            description=h.get("snippet") or "",
            matched_query=query,
        ))
    return jobs


def relevant_to_queries(job: Job, queries: list[str]) -> tuple[bool, str]:
    blob = job.search_blob
    title = clean_text(job.title).lower()
    best, best_score, best_title_hits, best_body_hits = "", 0, 0, 0
    for q in queries:
        words = [w for w in re.findall(r"[\wåäöÅÄÖéÉ]+", q.lower()) if len(w) > 2]
        title_hits = sum(1 for w in words if w in title)
        body_hits = sum(1 for w in words if w in blob)
        score = 4 * title_hits + body_hits
        if score > best_score:
            best_score, best = score, q
            best_title_hits, best_body_hits = title_hits, body_hits
    # Remote feeds are broad. Require a title signal, or at least two query terms
    # in the body, before a job reaches the candidate-matching layer.
    return (best_title_hits >= 1 or best_body_hits >= 2), best


def source_lane(queries: list[str], defaults: dict, sources_cfg: dict) -> list[Job]:
    max_per = int(defaults.get("max_per_query", 20))
    location = defaults.get("location") or ""
    country = defaults.get("country") or "SE"
    jobs = []

    if sources_cfg["providers"]["platsbanken"].get("enabled", True):
        with ThreadPoolExecutor(max_workers=min(6, max(1, len(queries)))) as pool:
            future_to_query = {pool.submit(platsbanken, q, max_per): q for q in queries}
            for future in as_completed(future_to_query):
                q = future_to_query[future]
                try:
                    jobs.extend(future.result())
                except Exception as e:
                    print(f"WARN platsbanken {q}: {e}")

    remote_sources = [
        ("remotive", remotive_all),
        ("remoteok", remoteok_all),
        ("weworkremotely", wwr_all),
    ]
    enabled_remote = [(name, fn) for name, fn in remote_sources if sources_cfg["providers"][name].get("enabled", True)]
    with ThreadPoolExecutor(max_workers=max(1, len(enabled_remote))) as pool:
        future_to_source = {pool.submit(fn): name for name, fn in enabled_remote}
        for future in as_completed(future_to_source):
            name = future_to_source[future]
            try:
                pool_jobs = future.result()
                for job in pool_jobs:
                    ok, q = relevant_to_queries(job, queries)
                    if ok:
                        job.matched_query = q
                        jobs.append(job)
            except Exception as e:
                print(f"WARN {name}: {e}")

    if sources_cfg["providers"]["adzuna"].get("enabled") and os.getenv("ADZUNA_APP_ID"):
        for q in queries[:8]:
            try:
                jobs.extend(adzuna(q, location=location, country=country.lower(), limit=max_per))
            except Exception as e:
                print(f"WARN adzuna {q}: {e}")

    if sources_cfg["providers"]["jooble"].get("enabled") and os.getenv("JOOBLE_API_KEY"):
        for q in queries[:5]:
            try:
                jobs.extend(jooble(q, location=location, limit=max_per))
            except Exception as e:
                print(f"WARN jooble {q}: {e}")

    return dedupe(jobs)


def _robots_allows(url: str, s: requests.Session) -> bool:
    p = urlparse(url)
    if not p.scheme or not p.netloc:
        return False
    rp = RobotFileParser()
    try:
        rr = s.get(f"{p.scheme}://{p.netloc}/robots.txt", timeout=10)
        rp.parse(rr.text.splitlines() if rr.ok else [])
    except Exception:
        rp.parse([])
    return rp.can_fetch(UA, url)


def fetch_public_job(url: str, supplied_text: str = "") -> Job:
    if supplied_text.strip():
        return Job(source="manual", title="", url=url, description=supplied_text.strip())

    s = session()
    if not _robots_allows(url, s):
        raise SourceError("robots.txt does not permit automated retrieval; paste the job text into the drill workflow instead.")

    r = s.get(url, timeout=TIMEOUT, allow_redirects=True)
    r.raise_for_status()
    if "html" not in (r.headers.get("content-type") or "").lower():
        raise SourceError("The URL is not an HTML job page.")

    soup = BeautifulSoup(r.text, "html.parser")
    posting = None
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            obj = json.loads(tag.string or tag.get_text() or "{}")
        except Exception:
            continue
        nodes = obj if isinstance(obj, list) else obj.get("@graph", []) if isinstance(obj, dict) and isinstance(obj.get("@graph"), list) else [obj]
        for node in nodes:
            if isinstance(node, dict) and str(node.get("@type", "")).lower() == "jobposting":
                posting = node
                break
        if posting:
            break

    for x in soup(["script", "style", "nav", "footer", "header", "form", "noscript"]):
        x.decompose()
    visible = clean_text(soup.get_text(" ", strip=True))

    if posting:
        org = posting.get("hiringOrganization") or {}
        loc = posting.get("jobLocation") or {}
        addr = loc.get("address") or {} if isinstance(loc, dict) else {}
        location = ", ".join(str(addr.get(k)) for k in ["addressLocality", "addressRegion", "addressCountry"] if addr.get(k))
        return Job(
            source=hostname(url),
            provider_id=str(posting.get("identifier") or ""),
            title=clean_text(posting.get("title")),
            company=clean_text(org.get("name") if isinstance(org, dict) else org),
            location=location,
            employment_type=clean_text(posting.get("employmentType")),
            published=clean_text(posting.get("datePosted")),
            deadline=clean_text(posting.get("validThrough")),
            url=r.url,
            description=clean_text(posting.get("description")) or visible,
            provider_meta={"jsonld": True},
        )

    return Job(source=hostname(url), title=clean_text(soup.title.get_text(" ", strip=True) if soup.title else ""), url=r.url, description=visible, provider_meta={"jsonld": False})


def hostname(url: str) -> str:
    return (urlparse(url).hostname or "public-url").replace("www.", "")
