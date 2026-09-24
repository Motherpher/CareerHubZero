from __future__ import annotations

import json
from pathlib import Path

from .learning import collect_outcome_events, derive_hypotheses
from .state import STATUS_LABELS, TERMINAL_STATUSES, rank_label


TEXT = {
    "sv": {
        "title": "{name} · CareerHub",
        "subtitle": "Hitta jobb → Analysera? → Sök",
        "find": "1 · Hitta jobb",
        "geo": "Geografisk drill",
        "analyse": "2 · Analysera?",
        "apply": "3 · Sök",
        "learning": "Karriärlärande",
        "history": "Historik",
        "active_hrdm": "Aktiva HRDM-rapporter",
        "hrdm_ledger": "HRDM-ledger",
        "job_vault": "Jobbvalv",
        "applications": "Ansökningar",
        "none": "Inga poster."
    },
    "en": {
        "title": "{name} · CareerHub",
        "subtitle": "Find jobs → Analyse? → Apply",
        "find": "1 · Find jobs",
        "geo": "Geographical drill",
        "analyse": "2 · Analyse?",
        "apply": "3 · Apply",
        "learning": "Career learning",
        "history": "History",
        "active_hrdm": "Active HRDM reports",
        "hrdm_ledger": "HRDM ledger",
        "job_vault": "Job vault",
        "applications": "Applications",
        "none": "No entries."
    }
}


def _t(language: str) -> dict:
    return TEXT.get(language, TEXT["sv"])


def _current_jobs(vault: dict) -> list[dict]:
    rows = [x for x in vault.get("jobs", []) if x.get("in_latest_scan")]
    return sorted(rows, key=lambda x: (-float(x.get("triage_score") or 0), x.get("deadline") or "9999"))


def _map_clusters(root: Path) -> list[dict]:
    for filename in ("country.json", "region.json", "world.json"):
        path = root / "data/maps" / filename
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return list(payload.get("clusters") or [])
        except Exception:
            pass
    return []


def render_control_room(path: Path, *, profile_name: str, language: str, vault: dict, cases: dict, hrdm_ledger: dict) -> None:
    tx = _t(language)
    jobs = _current_jobs(vault)
    active_cases = [x for x in cases.get("cases", []) if x.get("status") not in TERMINAL_STATUSES]
    active_hrdm = [x for x in hrdm_ledger.get("runs", []) if x.get("status") == "active"]
    hypotheses = derive_hypotheses(collect_outcome_events(cases))
    clusters = _map_clusters(path.parent)

    lines = [
        f"# {tx['title'].format(name=profile_name)}",
        "",
        f"**{tx['subtitle']}**",
        "",
        f"## {tx['find']}",
        "",
    ]
    if jobs:
        lines += [
            "| Roll | Arbetsgivare | Plats | Match | Sista dag | Varför |" if language == "sv"
            else "| Role | Employer | Location | Match | Deadline | Why |",
            "|---|---|---|---:|---|---|",
        ]
        for job in jobs[:30]:
            lines.append(
                f"| {job.get('title','')} | {job.get('company','')} | {job.get('location','')} | "
                f"{job.get('triage_score','')} | {str(job.get('deadline') or '-')[:10]} | "
                f"{'; '.join((job.get('triage_reasons') or [])[:2])} |"
            )
    else:
        lines.append(tx["none"])

    lines += ["", f"### {tx['geo']}", ""]
    if clusters:
        lines += [
            "| Område | Jobb | Nya |" if language == "sv" else "| Area | Jobs | New |",
            "|---|---:|---:|",
        ]
        for row in clusters[:25]:
            lines.append(f"| {row.get('label','')} | {row.get('count',0)} | {row.get('new_count',0)} |")
        lines += ["", "[Map data](data/maps/)"]
    else:
        lines.append("Geodata/kluster skapas när geotaggning körs." if language == "sv" else "Map clusters appear after geotagging runs.")

    lines += [
        "",
        f"## {tx['analyse']}",
        "",
        f"**[{tx['active_hrdm']}](HRDM_REPORTS.md)** · **[{tx['hrdm_ledger']}](HRDM_LEDGER.md)**",
        "",
    ]
    if active_hrdm:
        lines += [
            "| Roll | Arbetsgivare | Sista dag | Process-ID |" if language == "sv"
            else "| Role | Employer | Deadline | Process-ID |",
            "|---|---|---|---|",
        ]
        for row in active_hrdm[:20]:
            lines.append(
                f"| {row.get('title','')} | {row.get('company','')} | "
                f"{str(row.get('deadline') or '-')[:10]} | `{row.get('process_id','')}` |"
            )
    else:
        lines.append(tx["none"])

    lines += ["", f"## {tx['apply']}", ""]
    if active_cases:
        lines += [
            "| Prioritet | Roll | Arbetsgivare | Status | Nästa steg |" if language == "sv"
            else "| Priority | Role | Employer | Status | Next step |",
            "|---|---|---|---|---|",
        ]
        for case in active_cases:
            lines.append(
                f"| {rank_label(case.get('priority',3))} | {case.get('title','')} | {case.get('company','')} | "
                f"{STATUS_LABELS.get(case.get('status'), case.get('status',''))} | {case.get('next_action','')} |"
            )
    else:
        lines.append(tx["none"])

    lines += ["", f"## {tx['learning']}", ""]
    if hypotheses.get("event_count"):
        lines.append(
            "Lärandet påverkar endast sökhypoteser/rankning — aldrig kandidatfakta."
            if language == "sv"
            else "Learning affects search hypotheses/ranking only — never candidate truth."
        )
        lines.append("")
        for dim, rows in hypotheses.get("dimensions", {}).items():
            strongest = sorted(rows.items(), key=lambda x: abs(float(x[1].get("score") or 0)), reverse=True)[:5]
            if not strongest:
                continue
            lines.append(f"### {dim.replace('_',' ').title()}")
            for key, row in strongest:
                lines.append(
                    f"- {key}: {float(row.get('score') or 0):+.3f} "
                    f"(n={row.get('sample_size')}, confidence={row.get('confidence')})"
                )
            lines.append("")
    else:
        lines.append(tx["none"])

    lines += [
        "",
        f"## {tx['history']}",
        "",
        f"- [{tx['job_vault']}](JOB_VAULT.md)",
        f"- [{tx['applications']}](APPLICATIONS.md)",
        f"- [{tx['hrdm_ledger']}](HRDM_LEDGER.md)",
    ]
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def render_job_vault(path: Path, vault: dict) -> None:
    rows = list(vault.get("jobs", []))
    lines = [
        "# Job vault",
        "",
        f"Total ever seen: **{vault.get('total_jobs_ever_seen', len(rows))}**",
        "",
        "| Current | Role | Employer | Location | Match | First seen | Last seen |",
        "|---|---|---|---|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {'yes' if row.get('in_latest_scan') else 'no'} | {row.get('title','')} | "
            f"{row.get('company','')} | {row.get('location','')} | {row.get('triage_score','')} | "
            f"{str(row.get('first_seen') or '')[:10]} | {str(row.get('last_seen') or '')[:10]} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_applications(path: Path, cases: dict) -> None:
    rows = list(cases.get("cases", []))
    lines = [
        "# Applications",
        "",
        "| Role | Employer | Status | HRDM | External use | Next action |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('title','')} | {row.get('company','')} | {row.get('status','')} | "
            f"{row.get('hrdm_process_id') or '-'} | {row.get('external_use_allowed', False)} | "
            f"{row.get('next_action','')} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
