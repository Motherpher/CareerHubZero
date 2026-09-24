#!/usr/bin/env python3
"""FFOS Handyman — bounded deterministic repair executor."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from core import *

def select_findings(payload:dict,ids:list[str]|None)->list[dict]:
    rows=payload.get("findings",[])
    return [r for r in rows if not ids or r.get("finding_id") in ids]

class Handyman:
    def __init__(self,root:Path,household_manifest:Path,out_dir:Path):
        self.root=root.resolve(); self.cfg=load_json(household_manifest,{}) or {}; self.out=out_dir; self.repairs=self.cfg.get("repair_registry",{})
    def plan(self,finding:dict)->dict:
        rid=finding.get("repair_id"); spec=self.repairs.get(rid) if rid else None
        eligible=bool(spec and finding.get("repairability")=="J1" and spec.get("class")=="J1" and spec.get("command"))
        return {"finding_id":finding.get("finding_id"),"repair_id":rid,"eligible":eligible,"auto_repair":bool(spec and spec.get("auto_repair",False)),"allowed_paths":spec.get("allowed_paths",[]) if spec else [],"command":spec.get("command",[]) if spec else []}
    def apply(self,finding:dict)->dict:
        plan=self.plan(finding)
        if not plan["eligible"]: return {**plan,"state":"NOT_ELIGIBLE"}
        if worktree_changes(self.root): return {**plan,"state":"BLOCKED_DIRTY_WORKTREE","before_changes":worktree_changes(self.root)}
        spec=self.repairs[plan["repair_id"]]; result=run_command(self.root,spec["command"],int(spec.get("timeout",300)))
        changed=worktree_changes(self.root); allowed=set(spec.get("allowed_paths",[])); unauthorized=[p for p in changed if p not in allowed]; verification=[]
        if result["returncode"]==0 and not unauthorized:
            for v in spec.get("verify",[]): verification.append(run_command(self.root,v.get("command",[]),int(v.get("timeout",300))))
        ok=result["returncode"]==0 and not unauthorized and all(x["returncode"]==0 for x in verification)
        if unauthorized:
            for p in changed: git(self.root,"checkout","--",p)
            state="ROLLED_BACK_UNAUTHORIZED_PATH"
        elif not ok:
            for p in changed: git(self.root,"checkout","--",p)
            state="ROLLED_BACK_FAILED_VERIFY"
        elif changed: state="REPAIR_CANDIDATE"
        else: state="NO_CHANGE_REQUIRED"
        return {**plan,"state":state,"changed_paths":changed,"unauthorized_paths":unauthorized,"command_result":result,"verification":verification}
    def compatibility_wp(self,manifest_path:Path,wp:str,issues:list[dict])->dict:
        m=load_json(manifest_path,{}); cfg=m.get("work_packages",{}).get(wp,{})
        commands=cfg.get("repair_commands",[])
        if not commands: return {"state":"NO_REGISTERED_REPAIR_COMMANDS","rows":[]}
        if worktree_changes(self.root): return {"state":"BLOCKED_DIRTY_WORKTREE","rows":[]}
        rows=[]
        for spec in commands:
            cmd=spec if isinstance(spec,list) else spec.get("command",[]); timeout=300 if isinstance(spec,list) else int(spec.get("timeout",300))
            rows.append(run_command(self.root,cmd,timeout))
            if rows[-1]["returncode"]!=0: break
        changed=worktree_changes(self.root)
        return {"state":"REPAIR_CANDIDATE" if rows and all(r["returncode"]==0 for r in rows) else "FAILED","rows":rows,"changed_paths":changed,"issues":issues}

def main()->int:
    ap=argparse.ArgumentParser(description="FFOS Handyman")
    ap.add_argument("--root",default="."); ap.add_argument("--household-manifest",default="17-ffos/household/household-manifest.json"); ap.add_argument("--out",default=".ffos-household-output")
    ap.add_argument("--findings"); ap.add_argument("--finding",action="append"); ap.add_argument("--apply-safe",action="store_true"); ap.add_argument("--plan",action="store_true")
    ap.add_argument("--manifest"); ap.add_argument("--audit-dir"); ap.add_argument("--wp"); ap.add_argument("--issues-json")
    a=ap.parse_args(); root=Path(a.root).resolve(); h=Handyman(root,safe_path(root,a.household_manifest),safe_path(root,a.out)); h.out.mkdir(parents=True,exist_ok=True)
    if a.wp:
        if not a.manifest or a.issues_json is None: ap.error("--wp compatibility mode requires --manifest and --issues-json")
        res=h.compatibility_wp(safe_path(root,a.manifest),a.wp,json.loads(a.issues_json)); save_json(h.out/"handyman-latest.json",res); print(json.dumps(res,ensure_ascii=False))
        return 10 if res.get("state")=="REPAIR_CANDIDATE" else (0 if res.get("state")=="NO_CHANGE_REQUIRED" else 2)
    payload=load_json(safe_path(root,a.findings or ".ffos-household-output/findings-latest.json"),{}) or {}; rows=select_findings(payload,a.finding); plans=[h.plan(x) for x in rows]
    if not a.apply_safe:
        out={"state":"PLAN_ONLY","plans":plans}; save_json(h.out/"handyman-latest.json",out); print(json.dumps(out,ensure_ascii=False)); return 0
    results=[]
    for f in rows:
        p=h.plan(f)
        if p["eligible"] and p["auto_repair"]: results.append(h.apply(f))
    out={"state":"APPLIED_SAFE","results":results}; save_json(h.out/"handyman-latest.json",out); print(json.dumps(out,ensure_ascii=False))
    return 0 if all(r.get("state") in {"REPAIR_CANDIDATE","NO_CHANGE_REQUIRED"} for r in results) else 2
if __name__=="__main__": raise SystemExit(main())
