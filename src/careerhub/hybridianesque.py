from __future__ import annotations

from typing import Any

VALID_MODES = {"Auto", "Yes", "No"}

CRITERIA = (
    "plural_logics",
    "structural_asymmetry",
    "constitutive_translation",
    "materialized_output",
)

FAILURE_MODES = (
    "decorative_complexity_language",
    "prestige_coded_overload",
    "many_hats_drift",
    "undefined_outputs",
    "undefined_counterparties",
    "false_depth_through_blur",
)


def normalize_decision(value: str | None) -> str:
    if value in (None, ""):
        return "Auto"
    mode = str(value).strip()
    if mode not in VALID_MODES:
        raise ValueError("Hybridianesque mode must be 'Auto', 'Yes' or 'No'.")
    return mode


def empty_hyfilter(decision: str | None = None) -> dict[str, Any]:
    mode = normalize_decision(decision)
    return {
        "recommended": False,
        "evaluated": True,
        "activated": False,
        "confidence": "low",
        "activation_mode": "automatic" if mode == "Auto" else "expert_override",
        "activation_rationale": "Hybridianesque was evaluated but the semantic analysis did not complete.",
        "why": "",
        "criteria": {name: {"met": False, "evidence": []} for name in CRITERIA},
        "user_decision": None if mode == "Auto" else mode,
        "status": "not_recommended",
        "participating_logics": [],
        "asymmetries": [],
        "translation_relations": [],
        "process_to_output": [],
        "overload_or_misframing": [],
        "failure_modes": [],
        "risk_remaining": [],
        "framing_if_active": "",
    }


def _clear_deep_interpretation(data: dict[str, Any]) -> None:
    for key in (
        "participating_logics",
        "asymmetries",
        "translation_relations",
        "process_to_output",
        "overload_or_misframing",
        "failure_modes",
        "risk_remaining",
    ):
        data[key] = []
    data["framing_if_active"] = ""


def finalize_hyfilter(value: dict[str, Any] | None, decision: str | None = None) -> dict[str, Any]:
    mode = normalize_decision(decision)
    data = empty_hyfilter(mode)
    if isinstance(value, dict):
        data.update({k: v for k, v in value.items() if k in data})
        incoming_criteria = value.get("criteria")
        if isinstance(incoming_criteria, dict):
            for name in CRITERIA:
                if isinstance(incoming_criteria.get(name), dict):
                    data["criteria"][name] = {
                        "met": bool(incoming_criteria[name].get("met")),
                        "evidence": [str(x) for x in (incoming_criteria[name].get("evidence") or []) if str(x).strip()],
                    }

    met = [name for name in CRITERIA if data["criteria"][name]["met"]]
    evidenced = [name for name in met if data["criteria"][name]["evidence"]]
    threshold_met = len(met) >= 3 and len(evidenced) >= 3
    recommended = bool(data.get("recommended")) and threshold_met

    data["evaluated"] = True
    data["recommended"] = recommended
    data["activation_mode"] = "automatic" if mode == "Auto" else "expert_override"
    data["user_decision"] = None if mode == "Auto" else mode
    data["confidence"] = "high" if len(met) == 4 and len(evidenced) == 4 else "medium" if recommended else "low"

    if mode == "No":
        data["activated"] = False
        data["status"] = "declined" if recommended else "not_recommended"
        data["activation_rationale"] = (
            "Hybridianesque met the relevance threshold but was suppressed by an internal expert override."
            if recommended else
            "Hybridianesque was evaluated and did not meet the evidence threshold for activation."
        )
        _clear_deep_interpretation(data)
        return data

    data["activated"] = recommended
    if not recommended:
        data["status"] = "not_recommended"
        data["activation_rationale"] = (
            data.get("why") or
            "Hybridianesque was evaluated but not activated because the role did not meet the multi-logic, asymmetry, translation and output evidence threshold."
        )
        _clear_deep_interpretation(data)
        return data

    data["status"] = "active"
    data["activation_rationale"] = (
        data.get("why") or
        "Hybridianesque was activated automatically because the role met the evidence-based relevance threshold."
    )
    data["failure_modes"] = [x for x in list(data.get("failure_modes") or []) if x in FAILURE_MODES]
    return data
