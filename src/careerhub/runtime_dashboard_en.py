from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from dateutil import parser as dtparser

from .models import Job
from .state import STATUS_LABELS, TERMINAL_STATUSES, case_counts, rank_label


REPO = os.getenv("GITHUB_REPOSITORY", "")
PALETTE = {
    "paper": "#F7F8F3",
    "ink": "#111111",
    "cobalt": "#2E50E8",
    "blue": "#2A72A3",
    "pale": "#C6D8E6",
    "coral": "#F97279",
    "sun": "#F6AB16",
    "white": "#FFFFFF",
}


def save_public_jobs(path: Path, jobs: list[Job]):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(jobs),
        "jobs": [j.public_dict() for j in jobs],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def priority_label(index: int) -> str:
    if index < 4:
        return "Top lead"
    if index < 8:
        return "Good option"
    return "Explore"


def deadline_info(value: str) -> tuple[str, int | None]:
    if not value:
        return "No deadline shown", None
    try:
        d = dtparser.parse(str(value))
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        days = (d.date() - datetime.now(timezone.utc).date()).days
        label = d.strftime("%d %b")
        if days < 0:
            return f"{label} · closed", days
        if days == 0:
            return f"{label} · today", days
        if days == 1:
            return f"{label} · 1 day", days
        return f"{label} · {days} days", days
    except Exception:
        return str(value), None


def why_short(job: Job) -> str:
    reasons = []
    blob = job.search_blob
    if job.work_mode:
        reasons.append(job.work_mode)
    elif "remote" in blob or "distans" in blob:
        reasons.append("remote")
    if any(x in blob for x in ["part time", "part-time", "deltid"]):
        reasons.append("part-time")
    if job.matched_query:
        reasons.append(f"matches {job.matched_query}")
    return " · ".join(reasons[:2]) or "matched search profile"


def choose_link(job: Job, default_priority: int = 3) -> str:
    title = f"[CareerHub Job] {job.company or 'Employer'} — {job.title}"
    body = (
        "## CareerHub — Analyse this job\n\n"
        "Everything is already filled in. To start the HRDM analysis, click the green **Create issue** / **Submit new issue** button at the bottom of the page.\n\n"
        "### Job URL\n"
        f"{job.url}\n\n"
        "### Job ID\n"
        f"{job.id}\n\n"
        "### Role\n"
        f"{job.title}\n\n"
        "### Employer\n"
        f"{job.company}\n\n"
        "### Lane\n"
        f"{job.lane}\n\n"
        "### Priority 1–5\n"
        f"{default_priority}\n\n"
        "### Deadline\n"
        f"{job.deadline or ''}\n\n"
        "### Job text (optional)\n"
        "_Leave blank unless the site blocks automated retrieval._"
    )
    return f"https://github.com/{REPO}/issues/new?title={quote(title)}&body={quote(body)}"


def choose_any_link() -> str:
    return f"https://github.com/{REPO}/issues/new?template=careerhub-analyse-job.yml"


def status_update_link(case: dict, status: str) -> str:
    issue = int(case.get("issue_number") or 0)
    label = STATUS_LABELS.get(status, status)
    title = f"[CareerHub Update] #{issue} — {label}"
    body = (
        "### CareerHub case issue\n"
        f"{issue}\n\n"
        "### New status\n"
        f"{status}\n\n"
        "### Date\n"
        f"{datetime.now(timezone.utc).date().isoformat()}\n\n"
        "### Next action (optional)\n\n"
        "### Next action date (optional)\n"
    )
    return f"https://github.com/{REPO}/issues/new?title={quote(title)}&body={quote(body)}"


def lane_title(lane: str) -> tuple[str, str]:
    return {
        "core": ("Career-track", "Writing, reporting, editorial, communications, research and culture/NGO."),
        "adjacent": ("Adjacent", "Transferable content, coordination, research-support and communications work."),
        "bridge": ("Extra-income / flexible", "Part-time, temporary and lower-barrier work."),
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

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="560" viewBox="0 0 1200 560">
<rect width="1200" height="560" fill="{PALETTE["paper"]}"/>
<path d="M-80 90 C160 40 250 230 420 175 C585 122 565 390 730 328 C880 272 930 120 1280 220"
      fill="none" stroke="{PALETTE["cobalt"]}" stroke-width="92" stroke-linecap="round"/>
<text x="68" y="68" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="700" fill="{PALETTE["ink"]}" letter-spacing="2">CAREERHUB</text>
<text x="68" y="480" font-family="Arial, Helvetica, sans-serif" font-size="16" fill="{PALETTE["ink"]}">A three-step job journey</text>
<g transform="translate(110 122)">
  <circle cx="0" cy="0" r="70" fill="{PALETTE["paper"]}" stroke="{PALETTE["cobalt"]}" stroke-width="5"/>
  <text x="0" y="-12" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="19" font-weight="700" fill="{PALETTE["ink"]}">1 · FIND</text>
  <text x="0" y="21" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="38" font-weight="800" fill="{PALETTE["cobalt"]}">{found}</text>
  <text x="0" y="46" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="{PALETTE["ink"]}">live leads</text>
</g>
<g transform="translate(518 290)">
  <circle cx="0" cy="0" r="78" fill="{PALETTE["pale"]}" stroke="{PALETTE["blue"]}" stroke-width="5"/>
  <text x="0" y="-16" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="19" font-weight="700" fill="{PALETTE["ink"]}">2 · CHOOSE</text>
  <text x="0" y="23" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="40" font-weight="800" fill="{PALETTE["blue"]}">{chosen}</text>
  <text x="0" y="49" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="{PALETTE["ink"]}">active cases</text>
</g>
<g transform="translate(940 208)">
  <circle cx="0" cy="0" r="78" fill="{PALETTE["sun"]}" stroke="{PALETTE["ink"]}" stroke-width="4"/>
  <text x="0" y="-16" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="19" font-weight="700" fill="{PALETTE["ink"]}">3 · APPLY</text>
  <text x="0" y="23" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="40" font-weight="800" fill="{PALETTE["ink"]}">{applied}</text>
  <text x="0" y="49" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="{PALETTE["ink"]}">in process</text>
</g>
<g transform="translate(770 430)">
  <rect x="0" y="0" rx="25" width="350" height="74" fill="{PALETTE["coral"]}"/>
  <text x="24" y="31" font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="700" fill="{PALETTE["ink"]}">{active_deadlines} deadlines within 7 days</text>
  <text x="24" y="54" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="{PALETTE["ink"]}">{total_seen} jobs preserved in the historic vault</text>
</g>
</svg>'''
    path.write_text(svg, encoding="utf-8")


def render_job_vault(path: Path, vault: dict, cases_data: dict):
    cases_by_job = {c.get("job_id"): c for c in cases_data.get("cases", []) if c.get("job_id")}
    records = vault.get("jobs", [])
    active = [r for r in records if r.get("in_latest_scan")]
    historic = [r for r in records if not r.get("in_latest_scan")]
    lines = [
        "# Job Vault", "",
        f"**{len(records)} jobs preserved** · {len(active)} in the latest scan · {len(historic)} historical", "",
        "Nothing disappears when a new sourcing run replaces the shortlist. The full machine-readable history is in CareerHub/data/job_vault.json.", "",
        "## Current / recently sourced", "",
        "| Rank | Role | Employer | Deadline | First seen | Last seen | State | Action |",
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
            action = f"**[YES — Analyse]({choose_link(Job.from_dict(r), 3)})**"
        lines.append(f"| {rank} | [{title}]({url}) | {company} | {deadline} | {str(r.get('first_seen',''))[:10]} | {str(r.get('last_seen',''))[:10]} | active | {action} |")
    lines += ["", "## Historical / no longer in the latest shortlist", "", "| Role | Employer | Deadline | Last seen | State | Action |", "|---|---|---|---|---|---|"]
    for r in historic[:180]:
        deadline, _ = deadline_info(r.get("deadline", ""))
        title = str(r.get("title") or "").replace("|", "\\|")
        company = str(r.get("company") or "").replace("|", "\\|")
        url = r.get("url") or "#"
        case = cases_by_job.get(r.get("id"))
        if case:
            action = f"[case #{case.get('issue_number')}]({case.get('issue_url')})"
        else:
            action = f"**[YES — Analyse]({choose_link(Job.from_dict(r), 2)})**"
        lines.append(f"| [{title}]({url}) | {company} | {deadline} | {str(r.get('last_seen',''))[:10]} | {r.get('deadline_state') or 'historic'} | {action} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_applications(path: Path, cases_data: dict):
    cases = cases_data.get("cases", [])
    active = [c for c in cases if c.get("status") not in TERMINAL_STATUSES]
    closed = [c for c in cases if c.get("status") in TERMINAL_STATUSES]
    active.sort(key=lambda c: (-int(c.get("priority") or 3), c.get("deadline") or "9999"))
    lines = [
        "# Applications & Follow-up", "",
        "One chosen job becomes one CareerHub case. This is the process monitor after the job has left the sourcing board.", "",
        "## Active cases", "",
        "| Priority | Role | Employer | Status | Deadline | Next action | Next date | Case |",
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
        lines.append(f"| **{rank_label(c.get('priority'))}** | [{title}]({c.get('url') or issue_url}) | {company} | **{STATUS_LABELS.get(c.get('status'), c.get('status'))}** | {deadline} | {next_action} | {next_date} | [#{issue}]({issue_url}) |")
    lines += ["", "## Closed cases", "", "| Role | Employer | Outcome | Updated |", "|---|---|---|---|"]
    for c in closed[-60:]:
        lines.append(f"| {str(c.get('title') or '').replace('|','\\|')} | {str(c.get('company') or '').replace('|','\\|')} | {STATUS_LABELS.get(c.get('status'), c.get('status'))} | {str(c.get('status_updated_at') or '')[:10]} |")
    lines += ["", "## Status model", "", "Chosen → Preparing → Ready to apply → Applied → Contacted → Portfolio/Test → Interview/Meeting 1–5 → Offer / Denied / Withdrawn"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def case_actions(case: dict) -> str:
    status = case.get("status")
    if status in TERMINAL_STATUSES:
        return "—"
    actions = []
    if status in {"saved", "preparing", "ready"}:
        actions.append(f"[Mark applied]({status_update_link(case, 'applied')})")
    if status == "applied":
        actions.append(f"[Contacted]({status_update_link(case, 'contacted')})")
        actions.append(f"[Denied]({status_update_link(case, 'denied')})")
    if status in {"contacted", "portfolio"}:
        actions.append(f"[Interview 1]({status_update_link(case, 'interview_1')})")
        actions.append(f"[Meeting 1]({status_update_link(case, 'meeting_1')})")
        actions.append(f"[Portfolio/Test]({status_update_link(case, 'portfolio')})")
    if str(status).startswith("interview_"):
        n = int(str(status).split("_")[1])
        if n < 5:
            actions.append(f"[Interview {n+1}]({status_update_link(case, f'interview_{n+1}')})")
        actions.append(f"[Offer]({status_update_link(case, 'offer')})")
        actions.append(f"[Denied]({status_update_link(case, 'denied')})")
    if str(status).startswith("meeting_"):
        n = int(str(status).split("_")[1])
        if n < 5:
            actions.append(f"[Meeting {n+1}]({status_update_link(case, f'meeting_{n+1}')})")
        actions.append(f"[Interview 1]({status_update_link(case, 'interview_1')})")
        actions.append(f"[Offer]({status_update_link(case, 'offer')})")
    return " · ".join(actions[:3]) or f"[Update status](https://github.com/{REPO}/issues/new?template=careerhub-update-status.yml)"


def render_lane(lines: list[str], lane: str, jobs: list[Job], cases_by_job: dict):
    title, explanation = lane_title(lane)
    lines += [f"### {title}", "", explanation, ""]
    visible = jobs[:8]
    if not visible:
        lines += ["No current leads in this group.", ""]
        return
    lines += ["| Priority | Role | Employer | Deadline | Why | Analyse? |", "|---|---|---|---|---|---|"]
    for index, job in enumerate(visible):
        deadline, days = deadline_info(job.deadline)
        if days is not None and 0 <= days <= 3:
            deadline = f"**{deadline}**"
        title_txt = job.title.replace("|", "\\|")
        company = (job.company or "—").replace("|", "\\|")
        source_link = f"[{title_txt}]({job.url})" if job.url else title_txt
        if job.id in cases_by_job:
            c = cases_by_job[job.id]
            choose = f"Analysed · [open case #{c.get('issue_number')}]({c.get('issue_url')})"
        else:
            default_priority = 5 if index < 2 else 4 if index < 5 else 3
            choose = f"**Do you want to analyse this job? [YES →]({choose_link(job, default_priority)})**"
        lines.append(f"| {priority_label(index)} | {source_link} | {company} | {deadline} | {why_short(job).replace('|','\\|')} | {choose} |")
    lines += ["", f"_Showing the top {len(visible)} of {len(jobs)} current leads in this group._", ""]


def render_control_room(path: Path, jobs: list[Job], lane: str, cases_data: dict, vault: dict):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    by_lane = {"core": [j for j in jobs if j.lane == "core"], "adjacent": [j for j in jobs if j.lane == "adjacent"], "bridge": [j for j in jobs if j.lane == "bridge"]}
    cases = cases_data.get("cases", [])
    cases_by_job = {c.get("job_id"): c for c in cases if c.get("job_id")}
    active_cases = [c for c in cases if c.get("status") not in TERMINAL_STATUSES]
    active_cases.sort(key=lambda c: (-int(c.get("priority") or 3), c.get("deadline") or "9999"))
    lines = [
        "![CareerHub journey](visuals/careerhub-journey.svg)", "",
        "# CareerHub", "",
        "## 1 · FIND JOBS → 2 · CHOOSE JOB → 3 · APPLY", "",
        "Everything else—sourcing, ranking, HRDM, research, documents, reminders and follow-up—sits inside these three steps.", "",
        "---", "",
        "## 1 · Find jobs", "",
        f"**Last sourcing refresh:** {now} · **{len(jobs)} live leads** · **{vault.get('total_jobs_ever_seen', len(jobs))} jobs in the historic vault**", "",
        "**After pressing Refresh:** new results normally appear here in about **30–90 seconds**. The page changes only when the sourcing workflow has finished and committed the new shortlist.", "",
        f"**[Refresh jobs now →](https://github.com/{REPO}/actions/workflows/careerhub-scan.yml)** · **[Open historic Job Vault →](JOB_VAULT.md)** · **[Analyse a job I found elsewhere →]({choose_any_link()})**", "",
    ]
    for lane_name in ["core", "adjacent", "bridge"]:
        if lane == "all" or lane == lane_name:
            render_lane(lines, lane_name, by_lane[lane_name], cases_by_job)
    lines += [
        "---", "", "## 2 · Choose job", "",
        "**The only question is: Do you want to analyse this job?**", "",
        "If yes, press **YES — Analyse this job** beside the vacancy. CareerHub then handles the HRDM analysis, research, ranking, case creation and application pack in the background.", "",
        "You do not need to decide how HRDM should run or understand the case structure.", "",
    ]
    if active_cases:
        lines += ["| Rank | Job | Status | Deadline | Quick action |", "|---|---|---|---|---|"]
        for c in active_cases[:12]:
            deadline, days = deadline_info(c.get("deadline", ""))
            if days is not None and 0 <= days <= 3:
                deadline = f"**{deadline}**"
            issue_url = c.get("issue_url") or f"https://github.com/{REPO}/issues/{c.get('issue_number')}"
            title = str(c.get("title") or "").replace("|", "\\|")
            company = str(c.get("company") or "").replace("|", "\\|")
            lines.append(f"| **{c.get('priority',3)} / 5 · {rank_label(c.get('priority'))}** | [{title} — {company}]({issue_url}) | **{STATUS_LABELS.get(c.get('status'), c.get('status'))}** | {deadline} | {case_actions(c)} |")
    else:
        lines += ["No jobs analysed yet. Press **YES — Analyse this job** beside any vacancy above.", ""]
    lines += [
        "", f"**[Open full application/case monitor →](APPLICATIONS.md)**", "",
        "---", "", "## 3 · Apply", "",
        "Inside each chosen job CareerHub prepares the HRDM analysis, employer/role research, candidate positioning and editable Word draft.", "",
        "1. Open the CareerHub case.",
        "2. Download and edit the Word application pack.",
        "3. Submit the application to the employer.",
        "4. Click **Mark applied** here.",
        "5. Continue updating the case through Contacted, Portfolio/Test, Interview/Meeting 1–5, Offer or Denied.", "",
        "### Deadline reminders", "",
        "Chosen jobs can be reminded automatically before the application deadline. GitHub case reminders require no extra service. Optional email and SMS reminders can be enabled privately with repository secrets; contact details never need to be committed.", "",
        "**[Reminder setup →](SETUP.md#deadline-reminders)**", "",
        "---", "",
        "<details>", "<summary><strong>Profile, privacy and advanced controls</strong></summary>", "",
        "- [Review what CareerHub knows](profile/PROFILE_REVIEW.md)",
        "- [Privacy / recommended private operating mode](PRIVACY.md)",
        "- [Setup and notification options](SETUP.md)",
        "- [Source matrix](docs/SOURCE_MATRIX.md)",
        "- [HRDM-R specification](hrdm/HRDM_R_v6.3.md)", "",
        "</details>",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
