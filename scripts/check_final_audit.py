#!/usr/bin/env python3
import json,sys
from pathlib import Path

data=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if data.get("status") != "PASS":
    print("Final audit is not PASS:",data.get("status"))
    raise SystemExit(2)
if any(x.get("status") != "PASS" for x in data.get("work_packages",[])):
    print("At least one WP is not PASS")
    raise SystemExit(2)
print("CareerHub final audit PASS recorded.")
