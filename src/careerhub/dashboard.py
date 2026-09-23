from __future__ import annotations

from collections import Counter
from pathlib import Path
import html
import json

from .instance import load_instance


def build_dashboard_data(instance_file: str | Path) -> dict:
    data = load_instance(instance_file)
    cfg = data["instance"]
    jobs = data["job_vault"].get("jobs", [])
    applications = data["applications"].get("cases", data["applications"].get("applications", []))
    statuses = Counter(x.get("status", "unknown") for x in applications)
    return {
        "instance_id": cfg["careerhub"]["instance_id"],
        "engine": cfg["careerhub"]["engine"],
        "candidate": data["profile"].get("identity", {}).get("name", ""),
        "headline": data["profile"].get("positioning", {}).get("master_headline", ""),
        "jobs": len(jobs),
        "applications": len(applications),
        "status_counts": dict(statuses),
    }


def render_html(instance_file: str | Path, output: str | Path) -> Path:
    d = build_dashboard_data(instance_file)
    cards = [
        ("Jobs", d["jobs"]),
        ("Applications", d["applications"]),
        ("Applied", d["status_counts"].get("applied", 0)),
        ("Interviews", sum(v for k, v in d["status_counts"].items() if k.startswith(("interview_", "meeting_")))),
        ("Offers", d["status_counts"].get("offer", 0)),
    ]
    card_html = "".join(
        f'<div class="card"><div class="num">{value}</div><div>{html.escape(label)}</div></div>'
        for label, value in cards
    )
    body = (
        '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>CareerHub — {html.escape(d["candidate"])}</title>'
        '<style>body{font-family:system-ui;margin:0;background:#0d1117;color:#f0f3f6}main{max-width:1100px;margin:auto;padding:40px 22px}'
        '.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}.card{background:#161b22;border:1px solid #30363d;border-radius:14px;padding:18px}'
        '.num{font-size:30px;font-weight:700}.muted{color:#8b949e}</style></head><body><main>'
        f'<div class="muted">CareerHub profiled instance</div><h1>{html.escape(d["candidate"])}</h1><p>{html.escape(d["headline"])}</p>'
        f'<div class="grid">{card_html}</div>'
        '</main></body></html>'
    )
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(body, encoding="utf-8")
    output.with_suffix(".json").write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    return output
