#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from careerhub.application import fallback_application, run_ai_application, write_application_docx
from careerhub.hrdm import build_packet, fallback_hrdm, run_ai_hrdm
from careerhub.hrdm_reports import save_report_bundle
from careerhub.instance import load_profile_node
from careerhub.sources import fetch_public_job

ROOT = Path(__file__).resolve().parents[1]


def load_library_evidence(path: str) -> dict:
    if not path:
        return {"schema_version": "1.0", "source_count": 0, "sources": [], "source_ids": [], "source_hashes": []}
    file = Path(path)
    if not file.exists():
        return {"schema_version": "1.0", "source_count": 0, "sources": [], "source_ids": [], "source_hashes": []}
    data = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("sources", []), list):
        raise SystemExit("Library evidence context is invalid.")
    for source in data.get("sources", []):
        if source.get("status") != "ACTIVE" or not source.get("source_id") or not source.get("hash"):
            raise SystemExit("Library evidence context contains a non-ACTIVE or untraceable source.")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--text-file", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--company", default="")
    parser.add_argument("--deadline", default="")
    parser.add_argument("--lane", default="core")
    parser.add_argument("--out", required=True)
    parser.add_argument("--library-evidence-file", default="")
    args = parser.parse_args()

    manifest = Path(args.manifest).resolve()
    ctx = load_profile_node(manifest)
    root = ctx["root"]
    outdir = Path(args.out)
    if not outdir.is_absolute():
        outdir = root / outdir
    outdir.mkdir(parents=True, exist_ok=True)

    supplied_text = Path(args.text_file).read_text(encoding="utf-8") if args.text_file else ""
    job = fetch_public_job(args.url, supplied_text=supplied_text)
    if args.title and not job.title: job.title = args.title
    if args.company and not job.company: job.company = args.company
    if args.deadline and not job.deadline: job.deadline = args.deadline
    job.lane = args.lane

    library_evidence = load_library_evidence(args.library_evidence_file)
    packet = build_packet(job, ctx["profile"], args.lane, run_counter_path=root / "data/hrdm_runseq.json")
    packet["library_evidence"] = library_evidence
    packet["constraints"].extend([
        "Library evidence is user-owned, source-bounded analysis context; it does not mutate the verified candidate profile.",
        "Use Library evidence only when the source is ACTIVE and preserve source_id/hash attribution in reasoning.",
        "Do not treat storage-only, INACTIVE, failed-ingestion or absent Library sources as evidence.",
    ])

    evidence_manifest = {
        "schema_version": "1.0",
        "profile_id": library_evidence.get("profile_id"),
        "built_at": library_evidence.get("built_at"),
        "source_count": library_evidence.get("source_count", 0),
        "sources": [
            {key: source.get(key) for key in ("source_id", "filename", "document_class", "hash", "status", "extracted_text_ref", "char_count", "truncated")}
            for source in library_evidence.get("sources", [])
        ],
    }
    (outdir / "evidence_use_manifest.json").write_text(json.dumps(evidence_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (outdir / "job.json").write_text(json.dumps(job.full_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (outdir / "HRDM_input_packet.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    schema_path = ROOT / "core/hrdm/hrdm_result.schema.json"
    hrdm = run_ai_hrdm(packet, schema_path) or fallback_hrdm(packet)
    (outdir / "HRDM_result.json").write_text(json.dumps(hrdm, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_entry = save_report_bundle(root, hrdm, ctx["paths"]["hrdm_ledger"])

    ai_app = run_ai_application(job.full_dict(), ctx["profile"], hrdm, args.lane)
    app = ai_app or fallback_application(job.full_dict(), ctx["profile"], hrdm)
    (outdir / "application_package.json").write_text(json.dumps(app, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_application_docx(outdir, job.full_dict(), ctx["profile"], app)

    print(json.dumps({
        "process_id": packet["process_id"],
        "evidence_source_count": evidence_manifest["source_count"],
        "evidence_source_ids": [source["source_id"] for source in evidence_manifest["sources"]],
        "hrdm_report": report_entry["paths"],
        "ai_used": hrdm.get("ai_status") != "not_run",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
