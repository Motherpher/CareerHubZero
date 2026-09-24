#!/usr/bin/env python3
import json,sys
from pathlib import Path

path=Path(sys.argv[1]); key=sys.argv[2]
data=json.loads(path.read_text(encoding="utf-8"))
gate=(data.get("gates") or {}).get(key) or {}
if gate.get("status") != "PASS":
    print(f"{key}: {gate.get('status','MISSING')} - {gate.get('evidence','')}")
    raise SystemExit(2)
print(f"{key}: PASS - {gate.get('evidence','')}")
