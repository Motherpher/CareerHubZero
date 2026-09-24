#!/usr/bin/env python3
import json,sys
from pathlib import Path

data=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
profiles=data.get("profiles") or {}
failed=[]
for name in ("linus-fast","weronika-perez-borjas","grace"):
    row=profiles.get(name) or {}
    if row.get("central_body") is not True or row.get("local_motor_present") is True or row.get("compatibility") != "PASS":
        failed.append((name,row))
if failed:
    print("Profile cutover incomplete:", json.dumps(failed,ensure_ascii=False))
    raise SystemExit(2)
print("All active profiles are thin and centrally executed.")
