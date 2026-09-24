from __future__ import annotations

import json
import os
from pathlib import Path

from .hrdm_trace import create_reverse_trace, finalize_reverse_trace
from .hybridianesque import empty_hyfilter, finalize_hyfilter, normalize_decision
from .models import Job


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


def build_packet(
    job: Job,
    profile: dict,
    lane: str,
    *,
    run_counter_path: Path,
    hy_filter_decision: str | None = None,
) -> dict:
    decision = normalize_decision(hy_filter_decision)
    trace = create_reverse_trace(
        counter_path=run_counter_path,
        hy_filter_usage=decision == "Yes",
        environment="Standalone",
        piusite_usage=False,
        hcc_authority="HCC-Lite",
    )
    return {
        "process_id": trace["process_id"],
        "mode": "HRDM-R-v6.3",
        "lane": lane,
        "job": job.full_dict(),
        "candidate_evidence": public_candidate_evidence(profile),
        "hy_filter_decision": decision,
        "trace": trace,
        "constraints": [
            "Run the full HRDM-R sequence in canonical order.",
            "Do not invent candidate facts.",
            "Use only verified career sources and source-bound verified evidence as candidate facts.",
            "Private life, model memory, conversational impressions and search-only wishes are forbidden as candidate evidence.",
            "Separate job-ad facts from inference.",
            "Unknown candidate facts remain unknown.",
            "HCC-Lite must address structural honesty, overload, dignity, fairness, vulnerability sensitivity, non-deceptive framing and trace/accountability.",
            "Hybridianesque is an optional enclosed depth filter. Recommendation is semi-automatic; full use requires the exact user decision Yes.",
        ],
    }


def packet_prompt(packet: dict) -> str:
    decision = packet.get("hy_filter_decision")
    hy_instruction = (
        "The user explicitly answered Yes. If the four-criterion validity test supports it, run the full Hybridianesque filter."
        if decision == "Yes"
        else "The user explicitly answered No. You may record whether the filter would have been recommended, but do not run the deep filter."
        if decision == "No"
        else "No Hybridianesque decision has been supplied. Evaluate whether the filter is recommended. If recommended, set status awaiting_user_decision and do not perform the deep interpretation."
    )
    return f"""You are performing a full CareerHub HRDM-R v6.3 analysis.

Canonical Reverse sequence:
1 Ad/Text Intake
2 Signal Extraction
3 Key Words & Concepts
4 Hidden Need Reconstruction
5 Field Logic Reconstruction
6 FunctionCore Estimation
6A DoD Diagnostic
7 Likely Assessment Zones
8 Candidate Positioning Map
9 HCC Reverse Commentary

Candidate evidence rule:
- Only verified career evidence in the packet may be used as candidate facts or proof points.
- Never use private-life information, model memory, conversational impressions or search-only wishes as candidate evidence.
- Unknown means unknown.

HCC-Lite:
Review structural honesty, burden clarity, dignity/fairness, vulnerability sensitivity, non-deceptive framing and trace/accountability.

Hybridianesque (Hy-Filter):
- Status: optional depth filter; never globally active.
- Recommend only when the context plausibly contains the four criteria together:
  1) more than one logic genuinely in play,
  2) structural asymmetry is relevant,
  3) translation/mediation does constitutive work,
  4) process materializes into usable outputs.
- If active, identify participating logics, asymmetries, who/what translates between whom/what, process-to-output movement, overload/misframing, and remaining risk.
- Scan only these canonical failure modes:
  decorative_complexity_language, prestige_coded_overload, many_hats_drift,
  undefined_outputs, undefined_counterparties, false_depth_through_blur.
- Never glamorize overload, invent complexity, aestheticize incoherence or reward vagueness.
- Keep Hybridianesque logic enclosed in the hybridianesque output object.
- {hy_instruction}

Trace discipline:
- Preserve the supplied run_id, run sequence and trace identity.
- Do not invent a new Process-ID.
- The CareerHub runtime, not the model, finalizes the Process-ID state token after successful semantic execution.

Return only JSON conforming to the supplied schema.

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
    model = os.getenv("CAREERHUB_MODEL") or "gpt-5.6-sol"
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
    result = json.loads(response.output_text)
    result["hybridianesque"] = finalize_hyfilter(
        result.get("hybridianesque"),
        packet.get("hy_filter_decision"),
    )
    trace = finalize_reverse_trace(packet["trace"], success=True, warnings=[])
    trace["hy_filter_usage"] = result["hybridianesque"]["status"] == "active"
    result["trace"] = trace
    result["process_id"] = trace["process_id"]
    return result


def fallback_hrdm(packet: dict) -> dict:
    job = packet["job"]
    hy = empty_hyfilter(packet.get("hy_filter_decision"))
    warnings = ["Automated HRDM analysis not run."]
    trace = finalize_reverse_trace(packet["trace"], success=False, warnings=warnings)
    return {
        "process_id": trace["process_id"],
        "job": job,
        "ai_status": "not_run",
        "note": "OPENAI_API_KEY not configured. The HRDM run was registered but semantic analysis was not completed.",
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
            "gaps_unknowns": warnings,
            "prohibited_claims": [],
            "proof_points": [],
            "cv_emphasis": [],
        },
        "hybridianesque": hy,
        "hcc": {"risks": warnings, "commentary": "Not analysed."},
        "application_strategy": {
            "positioning": "",
            "opening": "",
            "evidence_to_use": [],
            "evidence_to_avoid": [],
            "tone": "",
            "interview_themes": [],
        },
        "trace": trace,
    }
