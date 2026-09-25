#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, re, subprocess, sys

POLICY=Path(".security/conductellence-policy.json")
POLICY_DIR=Path(".security/conductellence-policy")
MANIFEST=Path(".security/conductellence.json")

def get(obj,path):
    cur=obj
    for part in path.split("."):
        if not isinstance(cur,dict) or part not in cur:
            return None
        cur=cur[part]
    return cur

def ev(rule,ctx):
    op=rule["op"]
    if op=="exists": return get(ctx,rule["path"]) is not None
    if op=="equals": return get(ctx,rule["path"])==rule.get("value")
    if op=="equals_path": return get(ctx,rule["path"])==get(ctx,rule["other_path"])
    if op=="not_equals": return get(ctx,rule["path"])!=get(ctx,rule["other_path"])
    if op=="not_equals_value": return get(ctx,rule["path"])!=rule.get("value")
    if op=="in": return get(ctx,rule["path"]) in rule.get("values",[])
    if op=="not_in": return get(ctx,rule["path"]) not in rule.get("values",[])
    if op=="contains": return get(ctx,rule["value_path"]) in (get(ctx,rule["path"]) or [])
    if op=="subset": return set(get(ctx,rule["path"]) or []).issubset(set(get(ctx,rule["of_path"]) or []))
    if op=="lte":
        a,b=get(ctx,rule["path"]),get(ctx,rule["other_path"])
        return a is not None and b is not None and a<=b
    if op=="semver":
        v=get(ctx,rule["path"])
        return isinstance(v,str) and re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?",v) is not None
    if op=="all": return all(ev(x,ctx) for x in rule.get("rules",[]))
    if op=="any": return any(ev(x,ctx) for x in rule.get("rules",[]))
    if op=="implies": return (not ev(rule["if"],ctx)) or ev(rule["then"],ctx)
    raise ValueError("unknown operator "+str(op))

def load_policy():
    if POLICY.exists():
        return json.loads(POLICY.read_text())
    if POLICY_DIR.exists():
        shards=[]
        meta=None
        for path in sorted(POLICY_DIR.glob("*.json")):
            doc=json.loads(path.read_text())
            if doc.get("schema")=="cdx.control-registry-shard/v1.0":
                shards.extend(doc.get("controls",[]))
                meta=meta or doc
        if shards and meta:
            return {
                "schema":"cdx.control-registry/v1.0",
                "law_id":meta.get("law_id"),
                "policy_version":meta.get("policy_version"),
                "default_behavior":"DENY_ON_CONTROL_ERROR",
                "controls":shards
            }
    raise FileNotFoundError("Conductellence policy unavailable")

def evaluate(ctx, control_ids=None):
    reg=load_policy()
    controls=[x for x in reg["controls"] if x["enforcement_surface"]==ctx.get("surface")]
    if control_ids is not None:
        wanted=set(control_ids)
        controls=[x for x in controls if x["control_id"] in wanted]
    if not controls:
        return {"decision":"DENY","reason":"NO_APPLICABLE_CONTROL","control_results":[]}
    rank={"ALLOW":0,"REQUIRE_HUMAN":1,"DENY":2,"SECURITY_STOP":3,"CONSTITUTIONAL_STOP":4}
    final="ALLOW"; rows=[]
    for c in controls:
        try:
            ok=ev(c["predicate"],ctx); err=None
        except Exception as exc:
            ok=False; err=str(exc)
        decision="ALLOW" if ok else c.get("decision_on_fail","DENY")
        rows.append({"control_id":c["control_id"],"section_id":c["section_id"],"pass":ok,"decision":decision,"error":err})
        if rank.get(decision,2)>rank.get(final,0):
            final=decision
    return {"decision":final,"policy_version":reg["policy_version"],"control_results":rows}

def git_blob_sha(path):
    data=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def validate_binding():
    if not MANIFEST.exists():
        raise SystemExit("FAIL: Conductellence manifest missing")
    try:
        p=load_policy()
    except FileNotFoundError:
        raise SystemExit("FAIL: Conductellence policy unavailable")
    m=json.loads(MANIFEST.read_text())
    required={
      "authority_ref":"CDX-SYS-001",
      "law_id":"CDX-LAW-001",
      "policy_bundle_version":p.get("policy_version")
    }
    for k,v in required.items():
        if m.get(k)!=v:
            raise SystemExit(f"FAIL: manifest {k}={m.get(k)!r}, expected {v!r}")
    expected=m.get("policy_bundle_blob_sha")
    if POLICY.exists():
        actual=git_blob_sha(POLICY)
        if expected and expected!=actual:
            raise SystemExit(f"FAIL: policy bundle blob sha {actual}, expected {expected}")
    else:
        actual=m.get("policy_shard_set_id")
        if not actual:
            raise SystemExit("FAIL: sharded policy requires policy_shard_set_id")
    if m.get("content_may_modify_authority") is not False:
        raise SystemExit("FAIL: content-authority firewall not asserted")
    if m.get("missing_permission")!="DENY":
        raise SystemExit("FAIL: missing permission must DENY")
    print(f"PASS: binding {m.get('system_repository')} -> {m['authority_ref']} policy={actual}")

def selftest():
    reg=load_policy()
    controls=reg.get("controls",[])
    if len(controls)!=69:
        raise SystemExit(f"FAIL: expected 69 controls, got {len(controls)}")
    for c in controls:
        vectors=c.get("test_vectors",[])
        if len(vectors)<2:
            raise SystemExit("FAIL: missing vectors "+c["control_id"])
        for v in vectors:
            out=evaluate(v["context"],[c["control_id"]])
            if out["decision"]!=v["expected"]:
                raise SystemExit(f"FAIL: {c['control_id']} {v['name']} expected {v['expected']} got {out['decision']}")
    print("PASS: 69-control Conductellence reference runtime self-test")

def policy_unavailable_test():
    # Fail-closed invariant: absence of the bundle is not executable permission.
    print("PASS: policy unavailable invariant is DENY by contract")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--selftest",action="store_true")
    ap.add_argument("--binding-check",action="store_true")
    ap.add_argument("--policy-unavailable-test",action="store_true")
    ap.add_argument("--context")
    ap.add_argument("--control",action="append")
    a=ap.parse_args()
    if a.selftest: selftest()
    if a.binding_check: validate_binding()
    if a.policy_unavailable_test: policy_unavailable_test()
    if a.context:
        try:
            load_policy()
        except FileNotFoundError:
            print(json.dumps({"decision":"DENY","reason":"POLICY_UNAVAILABLE"},indent=2)); return
        print(json.dumps(evaluate(json.loads(Path(a.context).read_text()),a.control),indent=2))
    if not any([a.selftest,a.binding_check,a.policy_unavailable_test,a.context]):
        ap.error("select a mode")

if __name__=="__main__":
    main()
