#!/usr/bin/env python3
"""FFOS Janitor — repository entropy, drift, contradiction and hygiene controller."""
from __future__ import annotations
import argparse, json, os, re, sys, urllib.request
from pathlib import Path
from typing import Any
from core import *

TEXT_SUFFIXES={".md",".txt",".py",".yml",".yaml",".json",".toml",".ini",".cfg",".sql",".html",".css",".js",".ts"}
SECRET_PATTERNS=[
 ("PRIVATE_KEY",re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
 ("GITHUB_TOKEN",re.compile(r"(?:github_pat_|ghp_)[A-Za-z0-9_]{20,}")),
 ("OPENAI_KEY",re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
 ("AWS_KEY",re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
]
INCOMPLETE=("NOT YET EXECUTED","PLACEHOLDER — substantive completion required","TODO: SUBSTANTIVE COMPLETION")

class Janitor:
    def __init__(self,root:Path,manifest:Path,rules:Path,exceptions:Path,out_dir:Path):
        self.root=root.resolve(); self.manifest=load_json(manifest,{}) or {}; self.rules=load_json(rules,{}) or {}
        self.exceptions=load_json(exceptions,{"exceptions":[]}) or {"exceptions":[]}; self.out_dir=out_dir
        self.repository=self.manifest.get("repository",{}).get("id") or os.environ.get("GITHUB_REPOSITORY") or self.root.name
        self.findings:list[Finding]=[]
    def add(self,*args:Any,**kw:Any)->None: self.findings.append(make_finding(self.repository,"JANITOR",*args,**kw))
    def files(self):
        skip={".git",".ffos-household-output",".ffos-household-state","__pycache__"}
        for p in self.root.rglob("*"):
            if not p.is_file() or any(x in skip for x in p.parts): continue
            yield p
    def scan_json(self):
        for p in self.files():
            if p.suffix.lower()!=".json": continue
            try: json.loads(p.read_text(encoding="utf-8"))
            except Exception as exc:
                rel=str(p.relative_to(self.root))
                self.add("REPOSITORY","JSON-VALIDITY","CONTROL_DEFECT",[rel],str(exc),"valid JSON",repairability="J1",recommended_action="Repair JSON syntax before governed processing.")
    def scan_secrets(self):
        for p in self.files():
            if p.suffix.lower() not in TEXT_SUFFIXES or p.stat().st_size>2_000_000: continue
            txt=p.read_text(encoding="utf-8",errors="ignore")
            for kind,pat in SECRET_PATTERNS:
                if pat.search(txt):
                    rel=str(p.relative_to(self.root))
                    allowed=any(x.get("path")==rel and x.get("kind")==kind for x in self.manifest.get("janitor",{}).get("secret_fixture_allowlist",[]))
                    if allowed:
                        continue
                    self.add("SECURITY","SECRET-TRIPWIRE","SECURITY_STOP",[rel],kind,"no committed credential/private-key signature",confidence="MEDIUM",repairability="J2",recommended_action="Revoke/rotate if real; remove from history as required.",requires_human=True)
    def scan_hygiene(self):
        if not (self.root/".gitignore").exists():
            self.add("REPOSITORY","GITIGNORE-MISSING","HYGIENE",[".gitignore"],"missing","present",repairability="J1",repair_id="CREATE_GITIGNORE",blocks_progression=False,recommended_action="Install repository hygiene exclusions.")
        for p in self.files():
            if p.suffix.lower() not in {".md",".txt"}: continue
            txt=p.read_text(encoding="utf-8",errors="ignore")
            for marker in INCOMPLETE:
                if marker in txt and "99-archive" not in p.parts:
                    rel=str(p.relative_to(self.root))
                    self.add("REPOSITORY","SUBSTANTIVE-MARKER","DRIFT",[rel],marker,"no unresolved completion marker in active material",repairability="J2",blocks_progression=False,recommended_action="Confirm developmental status or complete/remove marker.")
                    break
    def scan_workflows(self):
        wf=self.root/".github/workflows/ffos-assurance.yml"
        if wf.exists() and "--repair" in wf.read_text(encoding="utf-8",errors="ignore"):
            self.add("CONTROL_PLANE","ASSURANCE-MUST-NOT-REPAIR","CONTROL_DEFECT",[str(wf.relative_to(self.root))],"acceptance invokes repair","immutable acceptance audit",repairability="J1",repair_id="REMOVE_ASSURANCE_REPAIR",recommended_action="Separate repair from acceptance.")
        wfd=self.root/".github/workflows"
        for p in wfd.glob("*.y*ml") if wfd.exists() else []:
            txt=p.read_text(encoding="utf-8",errors="ignore")
            hits=sorted(set(re.findall(r"uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@v\d+)\b",txt)))
            if hits:
                self.add("CI","MUTABLE-ACTION-MAJOR-TAG","HYGIENE",[str(p.relative_to(self.root))],hits,"SHA-pinned or explicitly accepted action references",repairability="J2",blocks_progression=False,recommended_action="Review and pin critical Actions references to immutable SHAs.")
    def source_value(self,spec:dict[str,Any])->Any:
        p=safe_path(self.root,spec["path"])
        if "pointer" in spec: return json_pointer(load_json(p),spec["pointer"])
        txt=p.read_text(encoding="utf-8",errors="ignore")
        m=re.search(spec["regex"],txt,re.MULTILINE)
        return m.group(int(spec.get("group",1))) if m else "__MISSING_MATCH__"
    def eval_rule(self,r:dict[str,Any]):
        typ=r["type"]; rid=r["id"]; sev=r.get("severity","DRIFT"); domain=r.get("domain","COHERENCE")
        common={"repairability":r.get("repairability","J2"),"repair_id":r.get("repair_id"),"blocks_progression":bool(r.get("blocks_progression",sev in BLOCKING_DEFAULT)),"requires_human":bool(r.get("requires_human",sev in {"SECURITY_STOP","CONSTITUTIONAL_STOP"})),"recommended_action":r.get("recommended_action","Resolve the governed inconsistency.")}
        if typ in {"version_consensus","json_equal"}:
            vals=[]; objs=[]
            for s in r["sources"]:
                try: v=self.source_value(s)
                except Exception as exc: v=f"__ERROR__:{exc}"
                vals.append({"label":s.get("label",s["path"]),"value":v}); objs.append(s["path"])
            unique={json.dumps(x["value"],sort_keys=True,default=str) for x in vals}
            if len(unique)>1 or any("__MISSING_MATCH__" in x for x in unique):
                expected="one governed release value across configured current-state claims" if typ=="version_consensus" else "equal values"
                self.add(domain,rid,sev,objs,vals,expected,canonical_source=r.get("canonical_source"),**common)
        elif typ=="closed_phase":
            p=safe_path(self.root,r["path"]); obj=load_json(p,{})
            state=json_pointer(obj,r.get("state_pointer","/state"))
            if state=="CLOSED":
                bad={}
                for ptr,expected in r.get("expect",{}).items():
                    try: actual=json_pointer(obj,ptr)
                    except Exception as exc: actual=f"__ERROR__:{exc}"
                    if actual!=expected: bad[ptr]={"actual":actual,"expected":expected}
                if bad: self.add(domain,rid,sev,[r["path"]],bad,r.get("expect",{}),**common)
        elif typ=="file_not_contains":
            p=safe_path(self.root,r["path"]); txt=p.read_text(encoding="utf-8",errors="ignore") if p.exists() else ""
            if r["text"] in txt: self.add(domain,rid,sev,[r["path"]],r["text"],"text absent",**common)
        elif typ=="path_exists":
            if not safe_path(self.root,r["path"]).exists(): self.add(domain,rid,sev,[r["path"]],"missing","present",**common)
    def scan_rules(self,profile:str="deep"):
        for r in self.rules.get("rules",[]):
            profiles=r.get("profiles",["deep","gate"])
            if profile not in profiles and "all" not in profiles: continue
            try: self.eval_rule(r)
            except Exception as exc:
                self.add("CONTROL_PLANE","JANITOR-RULE-ERROR","CONTROL_DEFECT",[r.get("id","UNKNOWN")],str(exc),"rule executes deterministically",repairability="J2",recommended_action="Repair Janitor rule configuration.")
    def scan_github(self):
        if not self.manifest.get("janitor",{}).get("github_api_checks",True): return
        token=os.environ.get("GITHUB_TOKEN"); repo=os.environ.get("GITHUB_REPOSITORY")
        if not token or not repo: return
        branch=self.manifest.get("repository",{}).get("default_branch","main")
        req=urllib.request.Request(f"https://api.github.com/repos/{repo}/branches/{branch}",headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json"})
        try:
            with urllib.request.urlopen(req,timeout=15) as resp: obj=json.loads(resp.read().decode())
            if not obj.get("protected",False):
                self.add("CONTROL_PLANE","DEFAULT-BRANCH-UNPROTECTED","CONTROL_DEFECT",[branch],"protected=false","protected branch with required acceptance checks",repairability="J2",blocks_progression=False,requires_human=True,recommended_action="Enable branch protection/ruleset and require governed CI.")
        except Exception as exc:
            self.add("CI","GITHUB-API-CHECK-UNAVAILABLE","INFO",[branch],str(exc),"GitHub API observable",repairability="J2",blocks_progression=False)
    def apply_exceptions(self):
        active=[]
        for f in self.findings:
            suppressed=False
            for ex in self.exceptions.get("exceptions",[]):
                if ex.get("rule_id")!=f.rule_id: continue
                target=ex.get("object")
                if target and target not in f.affected_objects: continue
                if ex.get("expires_at") and ex["expires_at"]<utc_now(): continue
                suppressed=True; break
            if not suppressed: active.append(f)
        self.findings=active
    def run(self,profile:str="deep")->list[Finding]:
        self.scan_json(); self.scan_secrets()
        if profile!="gate": self.scan_hygiene(); self.scan_workflows(); self.scan_github()
        self.scan_rules(profile); self.apply_exceptions(); return self.findings

def main()->int:
    ap=argparse.ArgumentParser(description="FFOS Janitor")
    ap.add_argument("--root",default="."); ap.add_argument("--manifest",default="17-ffos/household/household-manifest.json")
    ap.add_argument("--rules",default="17-ffos/household/janitor-rules.json"); ap.add_argument("--exceptions",default="17-ffos/household/exceptions.json")
    ap.add_argument("--out",default=".ffos-household-output"); ap.add_argument("--profile",choices=["deep","gate"],default="deep"); ap.add_argument("--json",action="store_true")
    a=ap.parse_args(); root=Path(a.root).resolve()
    try:
        j=Janitor(root,safe_path(root,a.manifest),safe_path(root,a.rules),safe_path(root,a.exceptions),safe_path(root,a.out))
        fs=j.run(a.profile); meta={"generated_at":utc_now(),"repository":j.repository,"head":git_head(root),"profile":a.profile}
        _,mp=write_report(j.out_dir,fs,meta)
        if a.json: print(json.dumps({"summary":summary(fs),"findings":[f.to_dict() for f in fs]},ensure_ascii=False))
        else: print(f"JANITOR findings={len(fs)} blocking={summary(fs)['blocking']} report={mp.relative_to(root)}")
        return exit_code(fs)
    except Exception as exc:
        print(f"JANITOR_CONFIG_ERROR: {exc}",file=sys.stderr); return 30
if __name__=="__main__": raise SystemExit(main())
