#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

# When a Python file under scripts/ is executed directly, Python places that
# directory before PYTHONPATH entries. Because scripts/careerhub.py exists,
# `import careerhub...` can otherwise resolve that file as a top-level module
# instead of the canonical src/careerhub package. Pin src/ first so this script
# is safe both in GitHub Actions and when invoked locally.
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / 'src'
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
else:
    sys.path.remove(str(SRC_ROOT))
    sys.path.insert(0, str(SRC_ROOT))

from careerhub.instance import load_profile_node, validate_profile_node_paths
from careerhub.models import Job
from careerhub.state import bind_analysis, choose_case


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--out', required=True, help='Output directory relative to the profile root or absolute')
    parser.add_argument('--case-id', type=int, required=True)
    parser.add_argument('--case-url', default='')
    parser.add_argument('--priority', type=int, default=3)
    args = parser.parse_args()

    manifest = Path(args.manifest).resolve()
    errors = validate_profile_node_paths(manifest)
    if errors:
        raise SystemExit('CareerHub profile-node validation failed:\n- ' + '\n- '.join(errors))
    ctx = load_profile_node(manifest)
    root = ctx['root']
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out

    job_path = out / 'job.json'
    packet_path = out / 'HRDM_input_packet.json'
    hrdm_path = out / 'HRDM_result.json'
    app_path = out / 'application_package.json'
    for required in [job_path, packet_path, hrdm_path, app_path]:
        if not required.exists():
            raise SystemExit(f'Missing drill output: {required}')

    job = Job.from_dict(json.loads(job_path.read_text(encoding='utf-8')))
    packet = json.loads(packet_path.read_text(encoding='utf-8'))
    hrdm = json.loads(hrdm_path.read_text(encoding='utf-8'))
    app = json.loads(app_path.read_text(encoding='utf-8'))

    choose_case(
        ctx['paths']['applications'],
        job,
        args.case_id,
        args.case_url,
        args.priority,
    )

    docx = next(iter(sorted(out.glob('Application_*.docx'))), None)
    application_paths = {'json': str(app_path.relative_to(root))}
    if docx:
        application_paths['docx'] = str(docx.relative_to(root))

    fallback_application_used = 'Den automatiska ansökningstexten kördes inte.' in str(app.get('cover_letter') or '')
    external_use_allowed = bool(hrdm.get('ai_status') != 'not_run' and not fallback_application_used)

    case = bind_analysis(
        ctx['paths']['applications'],
        args.case_id,
        str(packet.get('process_id') or ''),
        external_use_allowed=external_use_allowed,
        application_paths=application_paths,
    )
    print(json.dumps({
        'case_id': args.case_id,
        'process_id': packet.get('process_id'),
        'external_use_allowed': external_use_allowed,
        'application_paths': application_paths,
        'status': case.get('status'),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
