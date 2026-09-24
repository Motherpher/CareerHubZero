#!/usr/bin/env python3
"""FFOS Household controller — orchestration without authority merger."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from core import *
from janitor import Janitor
from handyman import Handyman
from director import Director,resolve_frontier
def scan(root:Path,out:Path,profile:str="deep"):
    j=Janitor(root,root/".ffos-household/household-manifest.json",root/".ffos-household/janitor-rules.json",root/".ffos-household/exceptions.json",out)
    fs=j.run(profile); write_report(out,fs,{"generated_at":utc_now(),"repository":j.repository,"head":git_head(root),"profile":profile}); return fs
def main()->int:
    ap=argparse.ArgumentParser(description="FFOS Household controller"); ap.add_argument("command",choices=["pulse","patrol","status"])
    ap.add_argument("--root",default="."); ap.add_argument("--out",default=".ffos-household-output"); ap.add_argument("--apply-safe",action="store_true")
    a=ap.parse_args(); root=Path(a.root).resolve(); out=safe_path(root,a.out)
    if a.command=="status":
        payload=load_json(out/"findings-latest.json",{}); print(json.dumps(payload.get("summary",{"state":"NO_REPORT"}),ensure_ascii=False)); return 0
    fs=scan(root,out,"deep")
    if a.command=="pulse":
        s=summary(fs); print(f"HOUSEHOLD PULSE findings={s['total']} blocking={s['blocking']}"); return exit_code(fs)
    if a.apply_safe:
        h=Handyman(root,root/".ffos-household/household-manifest.json",out); payload=load_json(out/"findings-latest.json",{}); results=[]
        for f in payload.get("findings",[]):
            p=h.plan(f)
            if p["eligible"] and p["auto_repair"]: results.append(h.apply(f))
        save_json(out/"handyman-latest.json",{"state":"PATROL_SAFE_REPAIRS","results":results})
        if any(r.get("state")=="REPAIR_CANDIDATE" for r in results): fs=scan(root,out,"deep")
    if not worktree_changes(root):
        m=load_json(root/".ffos-household/wp-manifest.json",{}); frontier=resolve_frontier(m)
        if frontier and not any(f.blocks_progression for f in fs):
            d=Director(root,root/".ffos-household/wp-manifest.json",root/".ffos-household/audit",root/".ffos-household/audit/director-state.json"); d.run(frontier,gate=True)
    s=summary(fs)
    for f in fs:
        print(f"HOUSEHOLD FINDING {f.severity} {f.rule_id} {f.finding_id} blocks={f.blocks_progression}")
    print(f"HOUSEHOLD PATROL findings={s['total']} blocking={s['blocking']} repairable_j1={s['repairable_j1']} changes={len(worktree_changes(root))}")
    return exit_code(fs)
if __name__=="__main__": raise SystemExit(main())
