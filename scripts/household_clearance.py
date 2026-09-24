#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from datetime import datetime, timezone
from pathlib import Path

BLOCKING={"CONTRADICTION","CONTROL_DEFECT","SECURITY_STOP","CONSTITUTIONAL_STOP"}

def load(path, default=None):
    if not path.exists(): return default
    return json.loads(path.read_text(encoding="utf-8"))

def now(): return datetime.now(timezone.utc).isoformat()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",default=".")
    ap.add_argument("--wp",default="all")
    ap.add_argument("--out",default=".careerhub-household-output")
    args=ap.parse_args()
    root=Path(args.root).resolve()
    manifest=load(root/"governance/household/manifest.json",{})
    state=load(root/"governance/household/wp-state.json",{})
    controls=load(root/"governance/household/external-controls.json",{}).get("controls",{})
    sequence=manifest.get("policy",{}).get("sequence",[])
    wanted=sequence if args.wp=="all" else [args.wp]
    results=[]
    accepted=set()

    # Existing committed PASS values remain accepted dependencies.
    for wp,row in state.get("work_packages",{}).items():
        if row.get("clearance")=="PASS":
            accepted.add(wp)

    for wp in wanted:
        cfg=manifest["work_packages"][wp]
        steps=[]
        findings=[]
        steps.append({"state":"DISPATCHED","at":now()})

        steps.append({"state":"JANITOR_SCAN","at":now()})
        for rel in cfg.get("required_paths",[]):
            if not (root/rel).exists():
                findings.append({
                    "role":"JANITOR","severity":"CONTROL_DEFECT","repairability":"J2",
                    "code":"MISSING_REQUIRED_PATH","object":rel
                })

        # Repository-wide central hygiene checks.
        if wp=="WP01":
            for rel in ("scripts/sync_stack_versions.py","scripts/check_stack_version.py"):
                p=root/rel
                if p.exists() and "deprecated" not in p.read_text(encoding="utf-8",errors="ignore").lower():
                    findings.append({
                        "role":"JANITOR","severity":"DRIFT","repairability":"J1",
                        "code":"LEGACY_STACK_PATH_ACTIVE","object":rel
                    })
        if wp=="WP02":
            ctl=controls.get("private_action_profile_execution",{})
            if ctl.get("state")!="PASS":
                findings.append({
                    "role":"JANITOR","severity":"CONTROL_DEFECT","repairability":"J2",
                    "code":"PRIVATE_ACTION_ACCESS_BLOCKED","object":"Motherpher/CareerHubZero Actions access",
                    "evidence":ctl.get("evidence",[])
                })
        if wp=="WP03":
            ctl=controls.get("profile_cutover",{})
            if ctl.get("state")!="PASS":
                findings.append({
                    "role":"JANITOR","severity":"CONTROL_DEFECT","repairability":"J2",
                    "code":"PROFILE_CUTOVER_NOT_PROVEN","object":"Grace/Weronika local motors",
                    "evidence":ctl.get("evidence",[])
                })

        steps.append({"state":"HANDYMAN_PLAN","at":now()})
        j1=[f for f in findings if f.get("repairability")=="J1"]
        steps.append({
            "state":"HANDYMAN_J1_APPLIED_OR_SKIPPED","at":now(),
            "result":"SKIPPED_NO_REGISTERED_J1" if not j1 else "J1_REQUIRES_REGISTERED_REPAIR"
        })

        steps.append({"state":"JANITOR_RESCAN","at":now()})
        steps.append({"state":"DIRECTOR_RECONCILIATION","at":now()})

        dep_block=[d for d in cfg.get("depends_on",[]) if d not in accepted]
        blockers=[f for f in findings if f.get("severity") in BLOCKING]
        tests_ok=os.environ.get("CAREERHUB_TESTS_PASS")=="1"
        if not tests_ok:
            blockers.append({
                "role":"DIRECTOR","severity":"CONTROL_DEFECT","repairability":"J2",
                "code":"REGRESSION_SUITE_NOT_CONFIRMED","object":"central tests"
            })

        if dep_block:
            clearance="BLOCKED_DEPENDENCY"
        elif blockers:
            clearance="BLOCKED"
        else:
            clearance="PASS"
            accepted.add(wp)

        steps.append({"state":"PASS_OR_BLOCKED","at":now(),"result":clearance})
        steps.append({"state":"CLOSED_OR_HELD","at":now(),"result":"CLOSED" if clearance=="PASS" else "HELD"})
        results.append({
            "wp":wp,"issue":cfg.get("issue"),"clearance":clearance,
            "dependencies":cfg.get("depends_on",[]),"dependency_blockers":dep_block,
            "findings":findings,"state_order":steps
        })

    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    payload={
        "schema_version":"1.0","generated_at":now(),
        "head":os.environ.get("GITHUB_SHA"),
        "results":results,
        "summary":{
            "pass":sum(1 for r in results if r["clearance"]=="PASS"),
            "blocked":sum(1 for r in results if r["clearance"]!="PASS")
        }
    }
    (out/"clearance.json").write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# CareerHub Household Clearance","",f"- Generated: {payload['generated_at']}",f"- HEAD: {payload['head'] or 'LOCAL'}",""]
    for r in results:
        lines += [f"## {r['wp']} — {r['clearance']}",f"- Issue: #{r['issue']}",f"- Dependencies: {', '.join(r['dependencies']) or 'none'}"]
        if r["dependency_blockers"]: lines.append(f"- Dependency blockers: {', '.join(r['dependency_blockers'])}")
        if r["findings"]:
            lines.append("- Findings:")
            for f in r["findings"]:
                lines.append(f"  - {f['severity']} / {f['repairability']} — {f['code']}: {f['object']}")
        lines.append("- Audit order: " + " → ".join(s["state"] for s in r["state_order"]))
        lines.append("")
    (out/"clearance.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(payload["summary"]))
    return 0 if payload["summary"]["blocked"]==0 else 20

if __name__=="__main__":
    raise SystemExit(main())
