from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from hashlib import sha1
from pathlib import Path

from .models import Job


def process_id(job: Job) -> str:
    seed = job.url or f"{job.company}|{job.title}"
    return f"HRDM-R-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{sha1(seed.encode()).hexdigest()[:8].upper()}"


def public_candidate_evidence(profile: dict) -> dict:
    verified_sources = {
        str(src.get("id")): src
        for src in profile.get("career_sources", [])
        if src.get("verification_status") == "verified"
    }
    verified_evidence = []
    for item in profile.get("evidence", []):
        source_ids = set(item.get("source_ids", []))
        if item.get("status") != "verified":
            continue
        if not source_ids or not source_ids.issubset(set(verified_sources)):
            continue
        verified_evidence.append(item)

    evidence_ids = {str(item.get("id")) for item in verified_evidence if item.get("id")}
    positioning = profile.get("positioning", {}) or {}
    derived = positioning.get("derived_from_evidence_ids", []) or []
    safe_positioning = positioning if set(derived).issubset(evidence_ids) else {}

    return {
        "identity": {"name": profile.get("identity", {}).get("name", "")},
        "career_sources": list(verified_sources.values()),
        "evidence": verified_evidence,
        "positioning": safe_positioning,
        "verification_queue": profile.get("verification_queue", []),
    }


def build_packet(job: Job, profile: dict, lane: str) -> dict:
    return {
        "process_id": process_id(job),
        "mode": "HRDM-R-v6.3",
        "lane": lane,
        "job": job.full_dict(),
        "candidate_evidence": public_candidate_evidence(profile),
        "constraints": [
            "Gå igenom hela matchningen systematiskt i rätt ordning.",
            "Hitta inte på uppgifter om kandidaten.",
            "Använd endast verifierade karriärkällor och source-bound verifierad evidens som kandidatfakta.",
            "Privatliv, modellminne, samtalsintryck och search-only önskemål får aldrig användas som kandidatfakta.",
            "Separate job-ad facts from inference.",
            "Bedömningen får bara använda verifierad karriärevidens i paketet.",
            "Språk, nuvarande plats och anställning som inte är verifierade ska markeras som okända.",
            "Bedöm avståndet till rollen, inte Grace värde eller kvalitet som person.",
            "HCC must address overload, ambiguity, fairness, dignity and structural honesty.",
        ],
    }


def packet_prompt(packet: dict) -> str:
    return f"""Du gör en fördjupad jobbmatchning i Karriärhubben.

Canonical sequence:
1 Ad/Text Intake
2 Signal Extraction
3 Key Words & Concepts
4 Hidden Need Reconstruction
5 Field Logic Reconstruction
6 FunctionCore Estimation
7 DoD Diagnostic
8 Likely Assessment Zones
9 Candidate Positioning Map
10 HCC Reverse Commentary

Använd webbkällor bara för aktuell offentlig information om arbetsgivaren och rollen. Använd inte webben för att fylla i kandidatens bakgrund.

Endast verifierade karriärkällor i kandidatpaketet får generera matchningsbara profilfakta eller HRDM proof points. Privatliv och användarens search-only "specifika önskemål eller behov" är uttryckligen förbjudna som kandidatbevis.

Om en karriäruppgift saknas ska den markeras som okänd eller som något att kontrollera.

Skriv alla användartexter på tydlig, vuxen och idiomatisk svenska. Undvik tekniskt språk i slutsatserna. Returnera enligt JSON-schemat.

PACKET:
{json.dumps(packet, ensure_ascii=False, indent=2)}
"""


def run_ai_hrdm(packet: dict, schema_path: Path) -> dict | None:
    if not os.getenv("OPENAI_API_KEY"):
        return None
    try:
        from openai import OpenAI
    except Exception:
        return None

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    model = os.getenv("CAREERHUB_MODEL") or "gpt-5.4"
    client = OpenAI()
    response = client.responses.create(
        model=model,
        store=False,
        tools=[{"type": "web_search", "search_context_size": "medium"}],
        input=packet_prompt(packet),
        text={
            "format": {
                "type": "json_schema",
                "name": "careerhub_hrdm",
                "strict": True,
                "schema": schema,
            }
        },
    )
    return json.loads(response.output_text)


def fallback_hrdm(packet: dict) -> dict:
    job = packet["job"]
    return {
        "process_id": packet["process_id"],
        "job": job,
        "ai_status": "not_run",
        "note": "OPENAI_API_KEY not configured. Use the generated HRDM prompt packet in ChatGPT or rerun after configuring the secret.",
        "signals": [],
        "concept_clusters": [],
        "hidden_need": {"statement": "", "confidence": "low", "rationale": []},
        "field_logic": {},
        "function_core": {"chain": "", "summary": ""},
        "dod": {
            "alpha": job.get("title", ""),
            "zenith": "",
            "dimensions": {"burden": 0, "scope_environment": 0, "function": 0, "signal_identity": 0},
            "average": 0,
            "classification": "Low",
        },
        "assessment_zones": [],
        "candidate_positioning": {
            "strong_matches": [],
            "transferable_matches": [],
            "gaps_unknowns": ["Automated HRDM analysis not run."],
            "prohibited_claims": [],
            "proof_points": [],
            "cv_emphasis": [],
        },
        "hcc": {"risks": [], "commentary": "Not analysed."},
        "application_strategy": {
            "positioning": "",
            "opening": "",
            "evidence_to_use": [],
            "evidence_to_avoid": [],
            "tone": "",
            "interview_themes": [],
        },
    }
