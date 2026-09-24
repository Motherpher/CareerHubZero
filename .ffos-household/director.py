#!/usr/bin/env python3
"""FFOS Director — immutable progression and acceptance controller."""
from __future__ import annotations
import argparse, json, shlex, sys
from pathlib import Path
from core import *
from janitor import Janitor

PASS={"PASS","REPAIRED_PASS"}
DEPENDENCY_ACCEPTED={"PASS","REPAIRED_PASS","DEFERRED_EXTERNAL_NON_BLOCKING","CLOSED_DIRECTOR_PASS","CLOSED_REFERENCE_BASELINE"}
BUILTIN={"dependency_pass","required_paths_exist","no_unresolved_machine_errors","audit_record_written"}

class Director:
    def __init__(self,root:Path,manifest:Path,audit:Path,state:Path,repair:bool=False):
        self.root=root.resolve(); self.manifest_path=manifest; self.audit=audit; self.state_path=state; self.repair=repair; self.m=load_json(manifest); self.state=load_json(state,{}) or {}
        if not self.m or not self.m.get("sequence"): raise ValueError("invalid manifest")
        self._validate_manifest()
    def _validate_manifest(self):
        seq=self.m["sequence"]; packs=self.m.get("work_packages",{})
        if len(seq)!=len(set(seq)): raise ValueError("duplicate WP IDs in sequence")
        missing=[x for x in seq if x not in packs]
        if missing: raise ValueError(f"missing work packages: {missing}")
    def path(self,rel:str)->Path: return safe_path(self.root,rel)
    def governed_worktree_changes(self)->list[str]:
        changes=worktree_changes(self.root)
        ignored=[]
        for p in (self.audit,self.state_path,self.root/".ffos-household-output"):
            try:
                rel=str(p.resolve().relative_to(self.root))
                ignored.append(rel.rstrip("/"))
            except Exception:
                pass
        return [p for p in changes if not any(p==x or p.startswith(x+"/") for x in ignored)]
    def check(self,chk:dict)->tuple[list[dict],list[dict]]:
        typ=chk["type"]; cid=chk.get("id",typ); rep=bool(chk.get("repairable",False)); issues=[]; evidence=[]
        if typ=="path_contains":
            p=self.path(chk["path"]); txt=p.read_text(encoding="utf-8",errors="ignore") if p.exists() else ""
            if chk["text"] not in txt: issues.append({"code":"REQUIRED_TEXT_MISSING","detail":cid,"repairable":rep})
        elif typ=="path_not_contains":
            p=self.path(chk["path"]); txt=p.read_text(encoding="utf-8",errors="ignore") if p.exists() else ""
            if chk["text"] in txt: issues.append({"code":"FORBIDDEN_TEXT_PRESENT","detail":cid,"repairable":rep})
        elif typ=="json_valid":
            try: json.loads(self.path(chk["path"]).read_text(encoding="utf-8"))
            except Exception as exc: issues.append({"code":"INVALID_JSON","detail":f"{cid}:{exc}","repairable":rep})
        elif typ=="command":
            ev=run_command(self.root,chk["command"],int(chk.get("timeout",300))); evidence.append(ev)
            if ev["returncode"]!=0: issues.append({"code":"COMMAND_FAILED","detail":cid,"repairable":rep})
        else: issues.append({"code":"UNKNOWN_CHECK","detail":cid,"repairable":False})
        return issues,evidence
    def scan(self,wp:str)->tuple[list[dict],list[dict]]:
        cfg=self.m["work_packages"][wp]; issues=[]; evidence=[]
        for dep in cfg.get("depends_on",[]):
            rs=self.state.get(dep,{}).get("status"); ms=self.m["work_packages"].get(dep,{}).get("state")
            if rs not in DEPENDENCY_ACCEPTED and ms not in DEPENDENCY_ACCEPTED: issues.append({"code":"DEPENDENCY_NOT_ACCEPTED","detail":dep,"repairable":False})
        for rel in cfg.get("required_paths",[]):
            p=self.path(rel)
            if not p.exists(): issues.append({"code":"MISSING_REQUIRED_PATH","detail":rel,"repairable":False}); continue
            if p.is_file() and p.suffix.lower() in {".md",".txt"}:
                txt=p.read_text(encoding="utf-8",errors="ignore")
                for marker in cfg.get("incomplete_markers",["NOT YET EXECUTED","PLACEHOLDER — substantive completion required","TODO: SUBSTANTIVE COMPLETION"]):
                    if marker in txt: issues.append({"code":"SUBSTANTIVE_COMPLETION_MISSING","detail":f"{rel}:{marker}","repairable":False}); break
        if cfg.get("require_acceptance_bindings",False):
            ids={x.get("id",x.get("type")) for x in cfg.get("checks",[])}; bindings=cfg.get("acceptance_bindings",{}) or {}
            for dim in cfg.get("acceptance",[]):
                if dim in BUILTIN: continue
                bound=bindings.get(dim,[])
                if not bound: issues.append({"code":"ACCEPTANCE_DIMENSION_UNBOUND","detail":dim,"repairable":False})
                for cid in bound:
                    if cid not in ids: issues.append({"code":"ACCEPTANCE_BINDING_UNKNOWN_CHECK","detail":f"{dim}:{cid}","repairable":False})
        for chk in cfg.get("checks",[]):
            i,e=self.check(chk); issues+=i; evidence+=e
        return issues,evidence
    def janitor_gate(self)->list[dict]:
        cfg_path=self.root/".ffos-household/household-manifest.json"
        if not cfg_path.exists(): return []
        cfg=load_json(cfg_path,{})
        if not cfg.get("director_gate",{}).get("enabled",False): return []
        j=Janitor(self.root,cfg_path,self.root/".ffos-household/janitor-rules.json",self.root/".ffos-household/exceptions.json",self.root/".ffos-household-output")
        findings=[f for f in j.run("gate") if f.blocks_progression]
        phase={}
        for key in ("phase_vi","phase_v","phase_iv","phase_iii","phase_ii"):
            candidate=self.m.get(key,{}) or {}
            if candidate.get("active_frontiers") or candidate.get("active_frontier") or candidate.get("status")=="ACTIVE":
                phase=candidate
                break
        allowed={x.get("rule_id") for x in phase.get("nonblocking_inherited_findings",[]) if x.get("rule_id")}
        return [{"code":"JANITOR_BLOCK","detail":f"{f.rule_id}:{f.finding_id}","repairable":False}
                for f in findings if f.rule_id not in allowed]
    def write_audit(self,wp:str,status:str,issues:list[dict],evidence:list[dict])->Path:
        d=self.audit/wp; d.mkdir(parents=True,exist_ok=True); p=d/f"{run_id()}-dispatch.md"; blocks=[]
        for ev in evidence: blocks.append(f"\nCommand: {shlex.join(ev['command'])}\nExit: {ev['returncode']}\n\n{ev['stdout']}{ev['stderr']}\n")
        p.write_text(f"# FFOS Director Dispatch Confirmation — {wp}\n\n- Status: **{status}**\n- Timestamp: {utc_now()}\n- Repository HEAD: {git_head(self.root) or 'UNKNOWN'}\n- Manifest SHA256: {sha256(self.manifest_path)}\n- Governed worktree clean: {not bool(self.governed_worktree_changes())}\n\n## Issues\n\n{json.dumps(issues,indent=2)}\n\n## Validation evidence\n"+''.join(blocks),encoding="utf-8")
        return p
    def run_one(self,wp:str,gate:bool=True)->str:
        cfg=self.m["work_packages"][wp]
        if cfg.get("state") in {"PLANNED_NOT_DISPATCHED","NOT_DISPATCHED"}: issues=[{"code":"WP_NOT_DISPATCHED","detail":wp,"repairable":False}]; ev=[]; status="NOT_DISPATCHED"
        elif cfg.get("progression_mode")=="DEFERRED_EXTERNAL_NON_BLOCKING": issues=[]; ev=[]; status="DEFERRED_EXTERNAL_NON_BLOCKING"
        else:
            issues,ev=self.scan(wp)
            if gate and not issues: issues+=self.janitor_gate()
            dirty=self.governed_worktree_changes()
            if dirty: issues.append({"code":"DIRTY_WORKTREE","detail":dirty,"repairable":False})
            if issues: status="BLOCKED"
            elif cfg.get("human_gate"): status="BLOCKED"; issues=[{"code":"HUMAN_ACCEPTANCE_REQUIRED","detail":wp,"repairable":False}]
            else: status="PASS"
        audit=self.write_audit(wp,status,issues,ev)
        self.state[wp]={"status":status,"timestamp":utc_now(),"audit":str(audit.relative_to(self.root)),"head":git_head(self.root)}; save_json(self.state_path,self.state)
        if status in PASS:
            seq=self.m["sequence"]; idx=seq.index(wp); nxt=seq[idx+1] if idx+1<len(seq) else "PROGRAMME COMPLETE"
            auto=bool(cfg.get("auto_dispatch_next",self.m.get("policy",{}).get("auto_dispatch",False)))
            if auto:
                (self.audit/wp/"DISPATCH-ORDER.md").write_text(f"# Dispatch Order — {wp}\n\nStatus: {status}\nNext: {nxt}\nAudit: {audit.relative_to(self.root)}\nTimestamp: {utc_now()}\n",encoding="utf-8")
            else:
                with audit.open("a",encoding="utf-8") as ah:
                    ah.write("\n\nAcceptance criteria passed; next work package is dependency-ready but NOT DISPATCHED.\n")
                (self.audit/wp/"NEXT-READY.md").write_text(f"# Next Ready — {wp}\n\nStatus: {status}\nNext ready: {nxt}\nDispatch state: NOT DISPATCHED\nAudit: {audit.relative_to(self.root)}\nTimestamp: {utc_now()}\n\nAcceptance criteria passed; next work package is dependency-ready but NOT DISPATCHED.\n",encoding="utf-8")
        return status
    def run(self,seq:list[str],gate:bool=True)->int:
        for wp in seq:
            s=self.run_one(wp,gate); print(f"{wp}: {s}")
            if s not in PASS|{"NOT_DISPATCHED","DEFERRED_EXTERNAL_NON_BLOCKING"} and self.m.get("policy",{}).get("stop_on_blocker",True): return 2
        return 0

def resolve_frontier(m:dict)->list[str]:
    for key in ("phase_vi","phase_v","phase_iv","phase_iii","phase_ii"):
        phase=m.get(key,{}) or {}; f=phase.get("active_frontiers") or phase.get("active_frontier")
        if f: return f if isinstance(f,list) else [f]
    return []

def main()->int:
    ap=argparse.ArgumentParser(description="FFOS Director")
    ap.add_argument("--all",action="store_true"); ap.add_argument("--frontier",action="store_true"); ap.add_argument("--wp")
    ap.add_argument("--repair",action="store_true",help="Deprecated: Director never mutates during acceptance")
    ap.add_argument("--root",default=str(Path(__file__).resolve().parents[3])); ap.add_argument("--manifest"); ap.add_argument("--audit-dir"); ap.add_argument("--state")
    a=ap.parse_args(); root=Path(a.root).resolve(); modes=sum(bool(x) for x in (a.all,a.frontier,a.wp))
    if modes!=1: ap.error("use exactly one of --all, --frontier or --wp")
    if a.repair: print("DIRECTOR_NOTICE: --repair is deprecated; acceptance is immutable. Use Handyman separately.",file=sys.stderr)
    man=Path(a.manifest or root/"17-ffos/director/wp-manifest.json"); aud=Path(a.audit_dir or root/"17-ffos/audit"); state=Path(a.state or aud/"director-state.json")
    try: d=Director(root,man,aud,state)
    except Exception as exc: print(f"CONFIG_ERROR: {exc}",file=sys.stderr); return 3
    if a.all: return d.run(d.m["sequence"],gate=False)
    if a.frontier:
        seq=resolve_frontier(d.m)
        if not seq: print("NO_ACTIVE_FRONTIER"); return 0
        return d.run(seq,gate=True)
    return d.run([a.wp],gate=True)
if __name__=="__main__": raise SystemExit(main())
