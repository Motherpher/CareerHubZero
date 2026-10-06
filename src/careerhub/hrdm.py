from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path

from .hrdm_trace import create_reverse_trace, finalize_reverse_trace
from .hybridianesque import empty_hyfilter, finalize_hyfilter, normalize_decision
from .models import Job


_FIELD_LOGIC_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "dominant_logics",
        "tensions",
        "coordination_requirements",
        "decision_environment",
        "implications_for_role",
        "summary",
    ],
    "properties": {
        "dominant_logics": {"type": "array", "items": {"type": "string"}},
        "tensions": {"type": "array", "items": {"type": "string"}},
        "coordination_requirements": {"type": "array", "items": {"type": "string"}},
        "decision_environment": {"type": "array", "items": {"type": "string"}},
        "implications_for_role": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"},
    },
}


def _strictify_openai_schema(schema: dict) -> dict:
    """Return an OpenAI Structured Outputs compatible view of the canonical schema.

    The canonical stored schema intentionally permits a few runtime-owned/free-form
    objects. Structured Outputs does not permit open-ended object keys in strict mode,
    so those objects are narrowed only for model generation. Runtime-owned values are
    restored after generation and the canonical schema remains the persistence contract.
    """
    strict = deepcopy(schema)
    properties = strict.get("properties", {})

    # The runtime already owns and restores the exact job packet. Asking the model to
    # recreate an open-ended provider metadata object is unnecessary and incompatible
    # with strict Structured Outputs.
    if "job" in properties:
        properties["job"] = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

    # Field logic is analytically meaningful, so replace the formerly free-form object
    # with a stable model-facing contract instead of collapsing it to an empty object.
    if "field_logic" in properties:
        properties["field_logic"] = deepcopy(_FIELD_LOGIC_OUTPUT_SCHEMA)

    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
            return
        if not isinstance(node, dict):
            return

        if node.get("type") == "object":
            object_properties = node.get("properties")
            if isinstance(object_properties, dict):
                node["additionalProperties"] = False
                # OpenAI strict JSON Schema requires every declared property to be
                # required. Optionality must instead be represented in the value type.
                node["required"] = list(object_properties.keys())
            else:
                # Canonical schemas may allow arbitrary string-key maps (for example
                # trace step IDs). The model does not own those maps; runtime restores
                # them after generation, so the strict model view is an empty object.
                node["properties"] = {}
                node["required"] = []
                node["additionalProperties"] = False

        for key, value in list(node.items()):
            if key == "additionalProperties" and isinstance(value, dict):
                # Replaced above for strict object maps; do not preserve an arbitrary
                # keyed-value schema in the model-facing contract.
                continue
            walk(value)

    walk(strict)
    return strict


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
    mode = normalize_decision(hy_filter_decision)
    trace = create_reverse_trace(
        counter_path=run_counter_path,
        hy_filter_usage=False,
        environment="Standalone",
        piusite_usage=False,
        hcc_authority="HCC-Lite",
    )
    trace["hy_filter_evaluated"] = True
    trace["hy_filter_activated"] = False
    return {
        "process_id": trace["process_id"],
        "mode": "HRDM-R-v6.3",
        "lane": lane,
        "job": job.full_dict(),
        "candidate_evidence": public_candidate_evidence(profile),
        "hy_filter_decision": mode,
        "trace": trace,
        "constraints": [
            "Run the full HRDM-R sequence in canonical order.",
            "Do not invent candidate facts.",
            "Use only verified career sources and source-bound verified evidence as candidate facts.",
            "Private life, model memory, conversational impressions and search-only wishes are forbidden as candidate evidence.",
            "Separate job-ad facts from inference.",
            "Unknown candidate facts remain unknown.",
            "HCC-Lite must address structural honesty, overload, dignity, fairness, vulnerability sensitivity, non-deceptive framing and trace/accountability.",
            "Hybridianesque relevance is evaluated automatically. Activate only when the evidence-based validity threshold is met.",
        ],
    }


def packet_prompt(packet: dict) -> str:
    mode = packet.get("hy_filter_decision") or "Auto"
    if mode == "No":
        hy_instruction = "Internal diagnostic override is No. Evaluate relevance, but suppress deep activation."
    elif mode == "Yes":
        hy_instruction = "Internal diagnostic override is Yes. Still require the evidence threshold; never force activation without it."
    else:
        hy_instruction = "Normal mode is Auto. You own the relevance judgement; do not ask the user whether to activate the filter."

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

Field Logic Reconstruction:
- Use the stable field_logic contract to identify dominant logics, tensions, coordination requirements, the decision environment, implications for the role and a concise synthesis.
- Do not use field_logic as a generic free-form dumping ground.

Hybridianesque (Hy-Filter):
- Evaluate it on every run, but it is not globally active.
- Recommend/activate only when at least three of these four criteria are genuinely evidenced, with explicit evidence for each met criterion:
  1) more than one logic genuinely in play,
  2) structural asymmetry is relevant,
  3) translation/mediation does constitutive work,
  4) process materializes into usable outputs.
- Do not activate merely because a role is senior, broad, multidisciplinary or rhetorically complex.
- If relevant, perform the full enclosed interpretation: participating logics, asymmetries, translation relations, process-to-output movement, overload/misframing, failure modes and remaining risk.
- Scan only these canonical failure modes: decorative_complexity_language, prestige_coded_overload, many_hats_drift, undefined_outputs, undefined_counterparties, false_depth_through_blur.
- Never glamorize overload, invent complexity, aestheticize incoherence or reward vagueness.
- In the schema-compatible `user_decision` field return null in Auto mode. Use status `active` when you recommend activation and `not_recommended` when you do not.
- {hy_instruction}

Trace discipline:
- Preserve the supplied run_id, run sequence and trace identity.
- Do not invent a new Process-ID.
- The CareerHub runtime, not the model, finalizes the Process-ID state token after successful semantic execution.
- The runtime is authoritative for the exact job object and trace map; model placeholders for those runtime-owned objects will be replaced after generation.

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

    canonical_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema = _strictify_openai_schema(canonical_schema)
    model = os.getenv("CAREERHUB_MODEL") or "gpt-5.6-sol"
    client = OpenAI()
    response = client.responses.create(
        model=model,
        store=False,
        tools=[{"type": "web_search", "search_context_size": "medium"}],
        input=packet_prompt(packet),
        text={"format": {"type": "json_schema", "name": "careerhub_hrdm", "strict": True, "schema": schema}},
    )
    result = json.loads(response.output_text)
    # Runtime-owned source-of-truth fields are restored exactly rather than trusting
    # a model-generated copy of profile/job metadata or process trace state.
    result["job"] = packet["job"]
    hy = finalize_hyfilter(result.get("hybridianesque"), packet.get("hy_filter_decision"))
    result["hybridianesque"] = hy
    trace = finalize_reverse_trace(packet["trace"], success=True, warnings=[])
    trace["hy_filter_usage"] = hy["status"] == "active"
    trace["hy_filter_evaluated"] = True
    trace["hy_filter_activated"] = hy["status"] == "active"
    trace["hy_filter_confidence"] = hy.get("confidence")
    trace["hy_filter_activation_rationale"] = hy.get("activation_rationale")
    trace["hy_filter_criteria"] = hy.get("criteria")
    result["trace"] = trace
    result["process_id"] = trace["process_id"]
    return result


def fallback_hrdm(packet: dict) -> dict:
    job = packet["job"]
    hy = empty_hyfilter(packet.get("hy_filter_decision"))
    warnings = ["Automated HRDM analysis not run."]
    trace = finalize_reverse_trace(packet["trace"], success=False, warnings=warnings)
    trace["hy_filter_evaluated"] = True
    trace["hy_filter_activated"] = False
    trace["hy_filter_confidence"] = "low"
    trace["hy_filter_activation_rationale"] = hy.get("activation_rationale")
    trace["hy_filter_criteria"] = hy.get("criteria")
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
        "dod": {"alpha": job.get("title", ""), "zenith": "", "dimensions": {"burden": 0, "scope_environment": 0, "function": 0, "signal_identity": 0}, "average": 0, "classification": "Low"},
        "assessment_zones": [],
        "candidate_positioning": {"strong_matches": [], "transferable_matches": [], "gaps_unknowns": warnings, "prohibited_claims": [], "proof_points": [], "cv_emphasis": []},
        "hybridianesque": hy,
        "hcc": {"risks": warnings, "commentary": "Not analysed."},
        "application_strategy": {"positioning": "", "opening": "", "evidence_to_use": [], "evidence_to_avoid": [], "tone": "", "interview_themes": []},
        "trace": trace,
    }
