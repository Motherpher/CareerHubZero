#!/usr/bin/env python3
"""Deterministic J1 repair primitives used by FFOS Handyman."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from core import load_json,save_json,json_pointer,json_pointer_set,safe_path
def main()->int:
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    c=sub.add_parser("json-copy"); c.add_argument("--root",default="."); c.add_argument("--source",required=True); c.add_argument("--source-pointer",required=True); c.add_argument("--target",required=True); c.add_argument("--target-pointer",required=True)
    s=sub.add_parser("json-set"); s.add_argument("--root",default="."); s.add_argument("--target",required=True); s.add_argument("--target-pointer",required=True); s.add_argument("--value",required=True)
    a=ap.parse_args(); root=Path(a.root).resolve()
    if a.cmd=="json-copy":
        src=load_json(safe_path(root,a.source)); tp=safe_path(root,a.target); target=load_json(tp); json_pointer_set(target,a.target_pointer,json_pointer(src,a.source_pointer)); save_json(tp,target)
    else:
        tp=safe_path(root,a.target); target=load_json(tp)
        try: value=json.loads(a.value)
        except Exception: value=a.value
        json_pointer_set(target,a.target_pointer,value); save_json(tp,target)
    return 0
if __name__=="__main__": raise SystemExit(main())
