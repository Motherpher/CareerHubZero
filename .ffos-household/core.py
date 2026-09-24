"""Shared FFOS Household runtime primitives. Standard library only."""
from __future__ import annotations
import hashlib, json, os, subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SEVERITY_ORDER={"INFO":0,"HYGIENE":1,"DRIFT":2,"CONTRADICTION":3,"CONTROL_DEFECT":4,"SECURITY_STOP":5,"CONSTITUTIONAL_STOP":6}
BLOCKING_DEFAULT={"CONTRADICTION","CONTROL_DEFECT","SECURITY_STOP","CONSTITUTIONAL_STOP"}

def utc_now()->str: return datetime.now(timezone.utc).isoformat()
def run_id()->str: return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
def load_json(path:Path,default:Any=None)->Any:
    if not path.exists(): return default
    return json.loads(path.read_text(encoding="utf-8"))
def save_json(path:Path,obj:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def sha256(path:Path)->str|None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
def safe_path(root:Path,rel:str)->Path:
    p=(root/rel).resolve(); p.relative_to(root.resolve()); return p
def git(root:Path,*args:str,timeout:int=60)->tuple[int,str,str]:
    try:
        cp=subprocess.run(["git",*args],cwd=root,capture_output=True,text=True,timeout=timeout)
        return cp.returncode,cp.stdout,cp.stderr
    except Exception as exc: return 126,"",str(exc)
def git_head(root:Path)->str|None:
    rc,out,_=git(root,"rev-parse","HEAD"); return out.strip() if rc==0 else None
def worktree_changes(root:Path)->list[str]:
    rc,out,_=git(root,"status","--porcelain")
    if rc: return []
    rows=[]
    for line in out.splitlines():
        if len(line)>=4:
            p=line[3:]
            if " -> " in p: p=p.split(" -> ",1)[1]
            rows.append(p)
    return sorted(set(rows))
def json_pointer(obj:Any,pointer:str)->Any:
    if pointer in ("","/"): return obj
    cur=obj
    for raw in pointer.lstrip("/").split("/"):
        key=raw.replace("~1","/").replace("~0","~")
        cur=cur[int(key)] if isinstance(cur,list) else cur[key]
    return cur
def json_pointer_set(obj:Any,pointer:str,value:Any)->None:
    parts=pointer.lstrip("/").split("/"); cur=obj
    for raw in parts[:-1]:
        key=raw.replace("~1","/").replace("~0","~")
        cur=cur[int(key)] if isinstance(cur,list) else cur[key]
    key=parts[-1].replace("~1","/").replace("~0","~")
    if isinstance(cur,list): cur[int(key)]=value
    else: cur[key]=value
def run_command(root:Path,command:list[str],timeout:int=300)->dict[str,Any]:
    try:
        cp=subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=timeout,env=os.environ.copy())
        return {"command":command,"returncode":cp.returncode,"stdout":cp.stdout,"stderr":cp.stderr}
    except subprocess.TimeoutExpired as exc:
        return {"command":command,"returncode":124,"stdout":exc.stdout or "","stderr":(exc.stderr or "")+f"\nTIMEOUT after {timeout}s"}
    except Exception as exc:
        return {"command":command,"returncode":126,"stdout":"","stderr":str(exc)}

@dataclass
class Finding:
    finding_id:str
    detected_at:str
    repository:str
    scanner:str
    domain:str
    rule_id:str
    severity:str
    confidence:str
    affected_objects:list[str]
    observed_state:Any
    expected_state:Any
    canonical_source:str|None=None
    evidence:list[str]|None=None
    repairability:str="J2"
    repair_id:str|None=None
    recommended_action:str=""
    blocks_progression:bool=False
    requires_human:bool=False
    first_seen:str|None=None
    last_seen:str|None=None
    occurrence_count:int=1
    resolved_at:str|None=None
    resolution_commit:str|None=None
    def to_dict(self)->dict[str,Any]: return asdict(self)

def finding_id(rule_id:str,objects:list[str],observed:Any)->str:
    raw=json.dumps([rule_id,objects,observed],sort_keys=True,default=str).encode()
    return "FIND-"+hashlib.sha256(raw).hexdigest()[:12].upper()
def make_finding(repository:str,scanner:str,domain:str,rule_id:str,severity:str,objects:list[str],observed:Any,expected:Any,**kw:Any)->Finding:
    ts=utc_now()
    return Finding(finding_id(rule_id,objects,observed),ts,repository,scanner,domain,rule_id,severity,kw.pop("confidence","HIGH"),objects,observed,expected,first_seen=ts,last_seen=ts,blocks_progression=kw.pop("blocks_progression",severity in BLOCKING_DEFAULT),requires_human=kw.pop("requires_human",severity in {"SECURITY_STOP","CONSTITUTIONAL_STOP"}),**kw)
def summary(findings:list[Finding])->dict[str,Any]:
    by={}
    for f in findings: by[f.severity]=by.get(f.severity,0)+1
    return {"total":len(findings),"blocking":sum(1 for f in findings if f.blocks_progression),"repairable_j1":sum(1 for f in findings if f.repairability=="J1"),"by_severity":by}
def exit_code(findings:list[Finding])->int:
    if any(f.blocks_progression for f in findings): return 20
    if findings: return 10
    return 0
def write_report(out_dir:Path,findings:list[Finding],meta:dict[str,Any])->tuple[Path,Path]:
    out_dir.mkdir(parents=True,exist_ok=True)
    payload={"meta":meta,"summary":summary(findings),"findings":[f.to_dict() for f in findings]}
    jp=out_dir/"findings-latest.json"; save_json(jp,payload)
    s=payload["summary"]
    lines=["# FFOS Household Janitor Report","",f"- Generated: {meta.get('generated_at')}",f"- Repository: {meta.get('repository')}",f"- HEAD: {meta.get('head') or 'UNKNOWN'}","","## Summary","",f"- Findings: **{s['total']}**",f"- Blocking: **{s['blocking']}**",f"- Constitutional stops: **{s['by_severity'].get('CONSTITUTIONAL_STOP',0)}**",f"- Security stops: **{s['by_severity'].get('SECURITY_STOP',0)}**",""]
    if findings:
        lines+=["## Findings",""]
        for f in sorted(findings,key=lambda x:(-SEVERITY_ORDER.get(x.severity,0),x.rule_id)):
            lines += [f"### {f.finding_id} — {f.rule_id}",f"- Severity: **{f.severity}**",f"- Domain: {f.domain}",f"- Blocks progression: {str(f.blocks_progression).lower()}",f"- Repairability: {f.repairability}",f"- Objects: {', '.join(f.affected_objects)}",f"- Observed: {json.dumps(f.observed_state,ensure_ascii=False,default=str)}",f"- Expected: {json.dumps(f.expected_state,ensure_ascii=False,default=str)}",f"- Action: {f.recommended_action or 'Inspect and resolve according to authority.'}",""]
    else: lines += ["**HOUSEHOLD CLEAR** — no findings."]
    mp=out_dir/"janitor-report-latest.md"; mp.write_text("\n".join(lines)+"\n",encoding="utf-8")
    return jp,mp
