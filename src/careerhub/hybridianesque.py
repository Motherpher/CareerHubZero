from __future__ import annotations

from typing import Any

VALID_DECISIONS = {"Yes", "No"}

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


def normalize_decision(value: str | None) -> str | None:
    if value in (None, ""):
        return None
    value = str(value).strip()
    if value not in VALID_DECISIONS:
        raise ValueError("Hybridianesque decision must be exactly 'Yes' or 'No'.")
    return value


def empty_hyfilter(decision: str | None = None) -> dict[str, Any]:
    decision = normalize_decision(decision)
    return {
        "recommended": False,
        "why": "",
        "criteria": {
            name: {"met": False, "evidence": []}
            for name in CRITERIA
        },
        "user_decision": decision,
        "status": "declined" if decision == "No" else "not_recommended",
        "participating_logics": [],
        "asymmetries": [],
        "translation_relations": [],
        "process_to_output": [],
        "overload_or_misframing": [],
        "failure_modes": [],
        "risk_remaining": [],
        "framing_if_active": "",
    }


def finalize_hyfilter(value: dict[str, Any] | None, decision: str | None = None) -> dict[str, Any]:
    """Enforce the HRDM v6.3 Hy-Filter gate and enclosure rule.

    Recommendation is semi-automatic. Full Hybridianesque interpretation is valid
    only after an explicit Yes. A No decision suppresses the deep interpretation.
    """
    decision = normalize_decision(decision)
    data = empty_hyfilter(decision)
    if isinstance(value, dict):
        data.update({k: v for k, v in value.items() if k in data})
        incoming_criteria = value.get("criteria")
        if isinstance(incoming_criteria, dict):
            for name in CRITERIA:
                if isinstance(incoming_criteria.get(name), dict):
                    data["criteria"][name] = {
                        "met": bool(incoming_criteria[name].get("met")),
                        "evidence": list(incoming_criteria[name].get("evidence") or []),
                    }

    met_count = sum(1 for name in CRITERIA if data["criteria"][name]["met"])
    data["recommended"] = bool(data.get("recommended")) and met_count >= 3
    data["user_decision"] = decision

    if not data["recommended"]:
        data["status"] = "not_recommended"
        data["participating_logics"] = []
        data["asymmetries"] = []
        data["translation_relations"] = []
        data["process_to_output"] = []
        data["overload_or_misframing"] = []
        data["failure_modes"] = []
        data["risk_remaining"] = []
        data["framing_if_active"] = ""
        return data

    if decision is None:
        data["status"] = "awaiting_user_decision"
        # Recommendation evidence may remain visible, but full deep interpretation
        # is enclosed until the user has explicitly answered Yes.
        data["participating_logics"] = []
        data["asymmetries"] = []
        data["translation_relations"] = []
        data["process_to_output"] = []
        data["overload_or_misframing"] = []
        data["failure_modes"] = []
        data["risk_remaining"] = []
        data["framing_if_active"] = ""
        return data

    if decision == "No":
        data["status"] = "declined"
        data["participating_logics"] = []
        data["asymmetries"] = []
        data["translation_relations"] = []
        data["process_to_output"] = []
        data["overload_or_misframing"] = []
        data["failure_modes"] = []
        data["risk_remaining"] = []
        data["framing_if_active"] = ""
        return data

    data["status"] = "active"
    data["failure_modes"] = [
        x for x in list(data.get("failure_modes") or [])
        if x in FAILURE_MODES
    ]
    return data
