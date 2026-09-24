from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

from dateutil import parser as dtparser

from .models import Job
from .state import STATUS_LABELS, TERMINAL_STATUSES, case_counts, rank_label


REPO = os.getenv("GITHUB_REPOSITORY", "")
PROFILE_NAME = os.getenv("CAREERHUB_PROFILE_NAME", "CareerHub")
PALETTE = {
    "paper": "#F4D59B",
    "ink": "#1B2220",
    "cobalt": "#063A3D",
    "blue": "#063A3D",
    "pale": "#F7F1E3",
    "coral": "#D94A3A",
    "sun": "#F2A000",
    "white": "#F7F1E3",
}


def save_public_jobs(path: Path, jobs: list[Job]):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(jobs),
        "jobs": [j.public_dict() for j in jobs],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def priority_label(job: Job) -> str:
    flags = set(job.review_flags or [])
    if "professional-licence-requirement-needs-verification" in flags or "degree-requirement-needs-verification" in flags:
        return "Kontrollera krav"
    score = float(job.triage_score or 0)
    if score >= 80:
        return "Stark träff"
    if score >= 70:
        return "Relevant"
    return "Möjlig"


def deadline_info(value: str) -> tuple[str, int | None]:
    if not value:
        return "Datum saknas", None
    try:
        d = dtparser.parse(str(value))
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        days = (d.date() - datetime.now(timezone.utc).date()).days
        months = ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
        label = f"{d.day} {months[d.month - 1]}"
        if days < 0:
            return f"{label} · stängd", days
        if days == 0:
            return f"{label} · idag", days
        if days == 1:
            return f"{label} · 1 dag", days
        return f"{label} · {days} dagar", days
    except Exception:
        return str(value), None


def why_short(job: Job) -> str:
    reasons = []
    blob = job.search_blob
    work_mode = (job.work_mode or "").lower()
    mode_labels = {"remote": "distans", "hybrid": "hybrid", "onsite": "på plats"}
    if work_mode:
        reasons.append(mode_labels.get(work_mode, work_mode))
    elif "remote" in blob or "distans" in blob:
        reasons.append("distans")
    if any(x in blob for x in ["part time", "part-time", "deltid"]):
        reasons.append("deltid")
    if job.matched_query:
        reasons.append(f"träff på {job.matched_query}")
    return " · ".join(reasons[:2]) or "relevant för sökningen"


def choose_link(job: Job, default_priority: int = 3) -> str:
    title = f"[CareerHub Job] {job.company or 'Arbetsgivare'} — {job.title}"
    lane_labels = {"core": "Huvudspår", "adjacent": "Närliggande möjlighet", "bridge": "Flexibelt / extra"}
    body = (
        "## Analysera det här jobbet\n\n"
        "Allt är förberett. När du vill starta analysen skapar du bara jobbsidan längst ned.\n\n"
        "### Länk till jobbet\n"
        f"{job.url}\n\n"
        "### Jobb-ID\n"
        f"{job.id}\n\n"
        "### Roll\n"
        f"{job.title}\n\n"
        "### Arbetsgivare\n"
        f"{job.company}\n\n"
        "### Spår\n"
        f"{lane_labels.get(job.lane, job.lane)}\n\n"
        "### Prioritet 1–5\n"
        f"{default_priority}\n\n"
        "### Sista ansökningsdag\n"
        f"{job.deadline or ''}\n\n"
        "### Jobbtext (valfritt)\n"
        "_Lämna tomt om länken går att läsa._"
    )
    return f"https://github.com/{REPO}/issues/new?title={quote(title)}&body={quote(body)}"


def choose_any_link() -> str:
    return f"https://github.com/{REPO}/issues/new?template=careerhub-analyse-job.yml"


def status_update_link(case: dict, status: str) -> str:
    issue = int(case.get("issue_number") or 0)
    label = STATUS_LABELS.get(status, status)
    title = f"[CareerHub Update] #{issue} — {label}"
    body = (
        "### Jobbsidans nummer\n"
        f"{issue}\n\n"
        "### Nytt läge\n"
        f"{label}\n\n"
        "### Datum\n"
        f"{datetime.now(ZoneInfo('Europe/Stockholm')).date().isoformat()}\n\n"
        "### Nästa steg\n\n"
        "### Datum för nästa steg\n"
    )
    return f"https://github.com/{REPO}/issues/new?title={quote(title)}&body={quote(body)}"


def lane_title(lane: str) -> tuple[str, str]:
    return {
        "core": ("Huvudspår", "Roller som ligger närmast den aktuella sökinriktningen."),
        "adjacent": ("Närliggande möjligheter", "Roller som ligger nära huvudspåret och kan vara värda att jämföra."),
        "bridge": ("Flexibelt / extra", "Alternativ med ett flexiblare upplägg eller en enklare väg in."),
    }.get(lane, (lane.title(), ""))


def render_visual(path: Path, jobs: list[Job], cases_data: dict, vault: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = case_counts(cases_data)
    active_deadlines = 0
    for job in jobs:
        _, days = deadline_info(job.deadline)
        if days is not None and 0 <= days <= 7:
            active_deadlines += 1

    found = len(jobs)
    chosen = counts["chosen"]
    applied = counts["applied"]
    total_seen = int(vault.get("total_jobs_ever_seen") or found)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="640" viewBox="0 0 1400 640" role="img" aria-label="{PROFILE_NAME} Karriärhubben">
<rect width="1400" height="640" fill="{PALETTE["paper"]}"/>
<rect width="390" height="640" fill="{PALETTE["cobalt"]}"/>
<circle cx="785" cy="245" r="220" fill="{PALETTE["sun"]}"/>
<rect x="1120" width="280" height="640" fill="{PALETTE["white"]}"/>
<rect x="1090" y="420" width="310" height="220" fill="{PALETTE["coral"]}"/>
<path d="M85 525 C250 385 365 350 535 365 C700 380 825 480 1015 420" fill="none" stroke="{PALETTE["white"]}" stroke-width="11" opacity=".86"/>

<text x="62" y="112" font-family="Arial, Helvetica, sans-serif" font-size="64" font-weight="300" letter-spacing="4" fill="{PALETTE["paper"]}">{PROFILE_NAME.upper()}</text>
<text x="65" y="173" font-family="Arial, Helvetica, sans-serif" font-size="27" font-weight="700" letter-spacing="8" fill="{PALETTE["sun"]}">KARRIÄRHUBBEN</text>
<text x="65" y="565" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="700" letter-spacing="3" fill="{PALETTE["paper"]}">TYDLIGT · VARMT · FRAMÅT</text>

<text x="475" y="88" font-family="Arial, Helvetica, sans-serif" font-size="25" font-weight="700" letter-spacing="5" fill="{PALETTE["cobalt"]}">NÄSTA STEG</text>
<text x="475" y="145" font-family="Georgia, serif" font-size="24" font-style="italic" fill="{PALETTE["ink"]}">Erfarenheten följer med. Riktningen kan förändras.</text>

<g transform="translate(475 245)">
  <text x="0" y="0" font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="700" letter-spacing="2" fill="{PALETTE["cobalt"]}">1 · HITTA JOBB</text>
  <text x="0" y="62" font-family="Arial, Helvetica, sans-serif" font-size="58" font-weight="300" fill="{PALETTE["cobalt"]}">{found}</text>
  <text x="0" y="90" font-family="Arial, Helvetica, sans-serif" font-size="15" fill="{PALETTE["ink"]}">aktuella möjligheter</text>
</g>

<g transform="translate(735 355)">
  <text x="0" y="0" font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="700" letter-spacing="2" fill="{PALETTE["cobalt"]}">2 · VÄLJ JOBB</text>
  <text x="0" y="62" font-family="Arial, Helvetica, sans-serif" font-size="58" font-weight="300" fill="{PALETTE["cobalt"]}">{chosen}</text>
  <text x="0" y="90" font-family="Arial, Helvetica, sans-serif" font-size="15" fill="{PALETTE["ink"]}">analyserade jobb</text>
</g>

<g transform="translate(1155 468)">
  <text x="0" y="0" font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="700" letter-spacing="2" fill="{PALETTE["white"]}">3 · SÖK</text>
  <text x="0" y="63" font-family="Arial, Helvetica, sans-serif" font-size="58" font-weight="300" fill="{PALETTE["white"]}">{applied}</text>
  <text x="0" y="91" font-family="Arial, Helvetica, sans-serif" font-size="15" fill="{PALETTE["white"]}">pågående</text>
</g>

<g transform="translate(1138 92)">
  <text x="0" y="0" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" letter-spacing="2" fill="{PALETTE["cobalt"]}">ÖVERSIKT</text>
  <text x="0" y="58" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="300" fill="{PALETTE["cobalt"]}">{active_deadlines}</text>
  <text x="0" y="82" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="{PALETTE["ink"]}">sista datum inom 7 dagar</text>
  <line x1="0" y1="112" x2="205" y2="112" stroke="{PALETTE["cobalt"]}" stroke-width="2" opacity=".45"/>
  <text x="0" y="160" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="300" fill="{PALETTE["cobalt"]}">{total_seen}</text>
  <text x="0" y="184" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="{PALETTE["ink"]}">jobb sparade i historiken</text>
</g>
</svg>'''
    path.write_text(svg, encoding="utf-8")

def render_job_vault(path: Path, vault: dict, cases_data: dict):
    cases_by_job = {c.get("job_id"): c for c in cases_data.get("cases", []) if c.get("job_id")}
    records = vault.get("jobs", [])
    active = [r for r in records if r.get("in_latest_scan")]
    historic = [r for r in records if not r.get("in_latest_scan")]
    lines = [
        "# Jobbhistorik", "",
        f"**{len(records)} jobb sparade** · {len(active)} i senaste sökningen · {len(historic)} historiska", "",
        "Inga jobb försvinner när en ny sökning ersätter den aktuella listan. Tidigare träffar sparas här för jämförelse.", "",
        "## Aktuella / nyligen hittade", "",
        "| Prioritet | Roll | Arbetsgivare | Sista dag | Först hittad | Senast sedd | Läge | Nästa steg |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in active[:100]:
        case = cases_by_job.get(r.get("id"))
        rank = rank_label(case.get("priority")) if case else "—"
        deadline, _ = deadline_info(r.get("deadline", ""))
        title = str(r.get("title") or "").replace("|", "\\|")
        company = str(r.get("company") or "").replace("|", "\\|")
        url = r.get("url") or "#"
        if case:
            action = f"[case #{case.get('issue_number')}]({case.get('issue_url')})"
        else:
            action = f"**[JA — Analysera]({choose_link(Job.from_dict(r), 3)})**"
        lines.append(f"| {rank} | [{title}]({url}) | {company} | {deadline} | {str(r.get('first_seen',''))[:10]} | {str(r.get('last_seen',''))[:10]} | aktuell | {action} |")
    lines += ["", "## Historik / inte längre i den aktuella listan", "", "| Roll | Arbetsgivare | Sista dag | Senast sedd | Läge | Nästa steg |", "|---|---|---|---|---|---|"]
    for r in historic[:180]:
        deadline, _ = deadline_info(r.get("deadline", ""))
        title = str(r.get("title") or "").replace("|", "\\|")
        company = str(r.get("company") or "").replace("|", "\\|")
        url = r.get("url") or "#"
        case = cases_by_job.get(r.get("id"))
        if case:
            action = f"[case #{case.get('issue_number')}]({case.get('issue_url')})"
        else:
            action = f"**[JA — Analysera]({choose_link(Job.from_dict(r), 2)})**"
        lines.append(f"| [{title}]({url}) | {company} | {deadline} | {str(r.get('last_seen',''))[:10]} | {r.get('deadline_state') or 'historic'} | {action} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_applications(path: Path, cases_data: dict):
    cases = cases_data.get("cases", [])
    active = [c for c in cases if c.get("status") not in TERMINAL_STATUSES]
    closed = [c for c in cases if c.get("status") in TERMINAL_STATUSES]
    active.sort(key=lambda c: (-int(c.get("priority") or 3), c.get("deadline") or "9999"))
    lines = [
        "# Ansökningar och uppföljning", "",
        "Här samlas de jobb du har valt att gå vidare med. Du ser nästa steg direkt och kan följa processen i din egen takt.", "",
        "## Pågående", "",
        "| Prioritet | Roll | Arbetsgivare | Läge | Sista dag | Nästa steg | Datum | Jobbsida |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for c in active:
        deadline, _ = deadline_info(c.get("deadline", ""))
        title = str(c.get("title") or "").replace("|", "\\|")
        company = str(c.get("company") or "").replace("|", "\\|")
        issue = c.get("issue_number")
        issue_url = c.get("issue_url") or f"https://github.com/{REPO}/issues/{issue}"
        next_action = str(c.get("next_action") or "—").replace("|", "\\|")
        next_date = str(c.get("next_action_date") or "—")[:10]
        lines.append(f"| **{rank_label(c.get('priority'))}** | [{title}]({c.get('url') or issue_url}) | {company} | **{case_status_label(c)}** | {deadline} | {next_action} | {next_date} | [#{issue}]({issue_url}) |")
    lines += ["", "## Avslutade", "", "| Roll | Arbetsgivare | Utfall | Uppdaterad |", "|---|---|---|---|"]
    for c in closed[-60:]:
        lines.append(f"| {str(c.get('title') or '').replace('|','\\|')} | {str(c.get('company') or '').replace('|','\\|')} | {STATUS_LABELS.get(c.get('status'), c.get('status'))} | {str(c.get('status_updated_at') or '')[:10]} |")
    lines += ["", "## Så följs en ansökan", "", "Valt → Förbereds → Redo att söka → Ansökan skickad → Kontakt → Arbetsprov/Test → Intervju/Möte 1–5 → Erbjudande / Avslutad / Avstår"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def case_status_label(case: dict) -> str:
    if case.get("audit_status") == "pre_firewall_revalidation_required" or case.get("external_use_allowed") is False:
        return "Kräver omvalidering"
    return STATUS_LABELS.get(case.get("status"), case.get("status"))


def case_actions(case: dict) -> str:
    status = case.get("status")
    if case.get("audit_status") == "pre_firewall_revalidation_required" or case.get("external_use_allowed") is False:
        return "Omvalidera först"
    if status in TERMINAL_STATUSES:
        return "—"
    actions = []
    if status in {"saved", "preparing", "ready"}:
        actions.append(f"[Ansökan skickad]({status_update_link(case, 'applied')})")
    if status == "applied":
        actions.append(f"[Kontakt]({status_update_link(case, 'contacted')})")
        actions.append(f"[Avslutad]({status_update_link(case, 'denied')})")
    if status in {"contacted", "portfolio"}:
        actions.append(f"[Intervju 1]({status_update_link(case, 'interview_1')})")
        actions.append(f"[Möte 1]({status_update_link(case, 'meeting_1')})")
        actions.append(f"[Arbetsprov/Test]({status_update_link(case, 'portfolio')})")
    if str(status).startswith("interview_"):
        n = int(str(status).split("_")[1])
        if n < 5:
            actions.append(f"[Intervju {n+1}]({status_update_link(case, f'interview_{n+1}')})")
        actions.append(f"[Erbjudande]({status_update_link(case, 'offer')})")
        actions.append(f"[Avslutad]({status_update_link(case, 'denied')})")
    if str(status).startswith("meeting_"):
        n = int(str(status).split("_")[1])
        if n < 5:
            actions.append(f"[Möte {n+1}]({status_update_link(case, f'meeting_{n+1}')})")
        actions.append(f"[Intervju 1]({status_update_link(case, 'interview_1')})")
        actions.append(f"[Erbjudande]({status_update_link(case, 'offer')})")
    return " · ".join(actions[:3]) or f"[Uppdatera läge](https://github.com/{REPO}/issues/new?template=careerhub-update-status.yml)"


def render_lane(lines: list[str], lane: str, jobs: list[Job], cases_by_job: dict):
    title, explanation = lane_title(lane)
    lines += [f"### {title}", "", explanation, ""]
    visible = jobs[:8]
    if not visible:
        lines += ["Inga aktuella jobb i den här gruppen just nu.", ""]
        return
    lines += ["| Prioritet | Roll | Arbetsgivare | Sista dag | Varför | Analysera? |", "|---|---|---|---|---|---|"]
    for index, job in enumerate(visible):
        deadline, days = deadline_info(job.deadline)
        if days is not None and 0 <= days <= 3:
            deadline = f"**{deadline}**"
        title_txt = job.title.replace("|", "\\|")
        company = (job.company or "—").replace("|", "\\|")
        source_link = f"[{title_txt}]({job.url})" if job.url else title_txt
        if job.id in cases_by_job:
            c = cases_by_job[job.id]
            choose = f"Analyserat · [öppna jobbsida #{c.get('issue_number')}]({c.get('issue_url')})"
        else:
            default_priority = 5 if index < 2 else 4 if index < 5 else 3
            choose = f"**Vill du analysera det här jobbet? [JA →]({choose_link(job, default_priority)})**"
        lines.append(f"| {priority_label(job)} | {source_link} | {company} | {deadline} | {why_short(job).replace('|','\\|')} | {choose} |")
    lines += ["", f"_Visar {len(visible)} av {len(jobs)} mest relevanta jobb i den här gruppen._", ""]


def render_control_room(path: Path, jobs: list[Job], lane: str, cases_data: dict, vault: dict):
    now_local = datetime.now(ZoneInfo("Europe/Stockholm"))
    months = ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
    now = f"{now_local.day} {months[now_local.month - 1]} {now_local.year} kl. {now_local.strftime('%H:%M')}"
    by_lane = {"core": [j for j in jobs if j.lane == "core"], "adjacent": [j for j in jobs if j.lane == "adjacent"], "bridge": [j for j in jobs if j.lane == "bridge"]}
    cases = cases_data.get("cases", [])
    cases_by_job = {c.get("job_id"): c for c in cases if c.get("job_id")}
    active_cases = [c for c in cases if c.get("status") not in TERMINAL_STATUSES]
    active_cases.sort(key=lambda c: (-int(c.get("priority") or 3), c.get("deadline") or "9999"))
    lines = [
        "![{PROFILE_NAME} · Karriärhubben](visuals/careerhub-journey.svg)", "",
        "# {PROFILE_NAME} · Karriärhubben", "",
        "## 1 · HITTA JOBB → 2 · VÄLJ JOBB → 3 · SÖK", "",
        "Välkommen. Här är dina aktuella möjligheter, samlade och förberedda. Du väljer tempot. Vi håller ordning på resten.", "",
        "---", "",
        "## 1 · Hitta jobb", "",
        f"**Senast uppdaterad:** {now} · **{len(jobs)} aktuella jobb** · **{vault.get('total_jobs_ever_seen', len(jobs))} jobb i historiken**", "",
        "**När du trycker på Uppdatera jobb:** nya jobb brukar synas här efter ungefär **30–90 sekunder**. Sidan uppdateras när sökningen är klar.", "",
        "När du vill kan du skriva **specifika önskemål eller behov** i sökningen. Det fungerar som ett extra raster för just sökningen och ändrar aldrig din karriärprofil.", "",
        f"**[Uppdatera jobb →](https://github.com/{REPO}/actions/workflows/careerhub-scan.yml)** · **[Öppna jobbhistoriken →](JOB_VAULT.md)** · **[Analysera ett jobb jag hittat själv →]({choose_any_link()})**", "",
    ]
    for lane_name in ["core", "adjacent", "bridge"]:
        if lane == "all" or lane == lane_name:
            render_lane(lines, lane_name, by_lane[lane_name], cases_by_job)
    lines += [
        "---", "", "## 2 · Välj jobb", "",
        "**När ett jobb väcker ditt intresse är frågan enkel: vill du analysera det?**", "",
        "När du vill titta närmare trycker du på **JA — Analysera**. Då går vi igenom rollen, arbetsgivaren, kraven och matchningen och förbereder nästa steg åt dig.", "",
        "Du behöver inte tänka på metoden bakom. När du vill gå vidare tar vi hand om analysen och presenterar det som är viktigt för dig.", "",
    ]
    if active_cases:
        lines += ["| Nivå | Jobb | Läge | Sista dag | Nästa steg |", "|---|---|---|---|---|"]
        for c in active_cases[:12]:
            deadline, days = deadline_info(c.get("deadline", ""))
            if days is not None and 0 <= days <= 3:
                deadline = f"**{deadline}**"
            issue_url = c.get("issue_url") or f"https://github.com/{REPO}/issues/{c.get('issue_number')}"
            title = str(c.get("title") or "").replace("|", "\\|")
            company = str(c.get("company") or "").replace("|", "\\|")
            lines.append(f"| **{c.get('priority',3)} / 5 · {rank_label(c.get('priority'))}** | [{title} — {company}]({issue_url}) | **{STATUS_LABELS.get(c.get('status'), c.get('status'))}** | {deadline} | {case_actions(c)} |")
    else:
        lines += ["Inga jobb är analyserade ännu. När något känns intressant väljer du **JA — Analysera**.", ""]
    has_revalidation_block = any(
        c.get("audit_status") == "pre_firewall_revalidation_required" or c.get("external_use_allowed") is False
        for c in active_cases
    )
    search_intro = (
        "Ett eller flera äldre ansökningsunderlag är spärrade tills verifierade karriärkällor finns och analysen har körts om."
        if has_revalidation_block
        else "När du vill söka ligger underlaget klart efter analysen: en tydlig matchning och ett redigerbart ansökningsutkast."
    )
    lines += [
        "", f"**[Öppna ansökningsöversikten →](APPLICATIONS.md)**", "",
        "---", "", "## 3 · Sök", "",
        search_intro, "",
        "1. Säkerställ att kandidatprofilen bygger på verifierade karriärkällor.",
        "2. Öppna jobbsidan och kör eller omkör analysen.",
        "3. Läs och justera det nya ansökningsunderlaget.",
        "4. Skicka först när underlaget är godkänt för extern användning.",
        "5. Följ sedan processen: kontakt, arbetsprov/test, intervju eller möte 1–5, erbjudande eller avslut.", "",
        "### När du vill hålla tempot", "",
        "Du kan få påminnelser före sista ansökningsdag och följa nästa steg direkt från jobbsidan. E-post och sms kan läggas till när du vill.", "",
        "**[Ställ in påminnelser →](SETUP.md#påminnelser)**", ""
        "---", "",
        "<details>", "<summary><strong>Profil och inställningar</strong></summary>", "",
        "- [Din arbetsprofil](profile/PROFILE_REVIEW.md)",
                "- [Inställningar och påminnelser](SETUP.md)",
        "- [Jobbkällor](docs/SOURCE_MATRIX.md)",
        "- [Fördjupad matchningslogik](hrdm/HRDM_R_v6.3.md)", "",
        "</details>",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
