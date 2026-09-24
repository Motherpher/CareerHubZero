from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .application import fallback_application, run_ai_application, write_application_docx
from .country_adapters import enrich_country_matrix
from .geography import GooglePlacesGeocoder, build_map_payload, geotag_vault
from .hrdm import build_packet, fallback_hrdm, packet_prompt, run_ai_hrdm
from .hrdm_reports import maintain_hrdm_reports, save_report_bundle
from .hub import render_applications as render_hub_applications, render_control_room as render_hub_control_room, render_job_vault as render_hub_job_vault
from .instance import load_profile_node, validate_profile_node_paths
from .learning import collect_outcome_events, derive_hypotheses, learning_bonus
from .matching import candidate_terms, rank_jobs
from .models import Job
from .search_contract import lane_queries, normalize_search
from .sources import fetch_public_job, load_yaml as load_source_yaml, source_lane
from .state import append_case_event, bind_analysis, choose_case, load_cases, merge_job_vault, update_case, update_priority, write_json

CENTRAL_ROOT = Path(__file__).resolve().parents[2]


def _manifest(path: str | Path) -> Path:
    return Path(path).resolve()


def _load_context(manifest: Path) -> dict:
    errors = validate_profile_node_paths(manifest)
    if errors:
        raise SystemExit("CareerHub profile-node validation failed:\n- " + "\n- ".join(errors))
    return load_profile_node(manifest)


def _language(ctx: dict) -> str:
    return str((ctx["manifest"].get("ui") or {}).get("language") or "sv")


def _render_all(ctx: dict, jobs: list[Job] | None = None, lane: str = "all") -> None:
    root = ctx["root"]
    profile_name = str((ctx["profile"].get("identity") or {}).get("name") or ctx["manifest"]["profile_id"])
    os.environ["CAREERHUB_PROFILE_NAME"] = profile_name

    if jobs is None:
        latest = root / "data/latest_jobs.json"
        payload = json.loads(latest.read_text(encoding="utf-8")) if latest.exists() else {"jobs": []}
        jobs = [Job.from_dict(x) for x in payload.get("jobs", [])]

    cases = load_cases(ctx["paths"]["applications"])
    vault = json.loads(ctx["paths"]["job_vault"].read_text(encoding="utf-8"))

    latest_path = root / "data/latest_jobs.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(
        json.dumps({"jobs": [j.public_dict() for j in jobs]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    maintain_hrdm_reports(
        root,
        ctx["paths"]["hrdm_ledger"],
        control_room=None,
    )
    ledger = json.loads(ctx["paths"]["hrdm_ledger"].read_text(encoding="utf-8"))
    render_hub_job_vault(root / "JOB_VAULT.md", vault)
    render_hub_applications(root / "APPLICATIONS.md", cases)
    render_hub_control_room(
        root / "CONTROL_ROOM.md",
        profile_name=profile_name,
        language=_language(ctx),
        vault=vault,
        cases=cases,
        hrdm_ledger=ledger,
    )


def cmd_validate(args):
    manifest = _manifest(args.manifest)
    errors = validate_profile_node_paths(manifest)
    if errors:
        for error in errors:
            print("ERROR", error)
        raise SystemExit(1)
    print("CareerHub profile node OK:", manifest)


def cmd_scan(args):
    manifest = _manifest(args.manifest)
    ctx = _load_context(manifest)
    profile = ctx["profile"]
    runtime = normalize_search(ctx["search"])
    source_cfg = load_source_yaml(CENTRAL_ROOT / "config/sources.default.yaml")

    overlay = (args.search_overlay or runtime["search_overlay"] or "").strip()
    selected = [x.strip() for x in args.lane.split(",")] if args.lane != "all" else []
    cterms = candidate_terms(profile)
    cases_data = load_cases(ctx["paths"]["applications"])
    outcome_events = collect_outcome_events(cases_data)
    hypotheses = derive_hypotheses(outcome_events)
    all_jobs: list[Job] = []

    for lane in runtime["lanes"]:
        bucket = lane["bucket"]
        lane_id = str(lane.get("lane_id") or bucket)
        if selected and bucket not in selected and lane_id not in selected:
            continue
        queries = lane_queries(lane, cterms, overlay)
        if not queries:
            continue
        sourced = source_lane(queries, runtime, source_cfg)
        ranked = rank_jobs(sourced, bucket, {"queries": queries}, profile, runtime, search_overlay=overlay)
        for job in ranked:
            job.provider_meta["search_lane_id"] = lane_id
            job.provider_meta["search_lane_name"] = lane.get("name") or lane_id
            job.provider_meta["query_provenance"] = {
                "lane_id": lane_id,
                "queries": queries,
                "matched_query": job.matched_query,
                "search_overlay_used": bool(overlay),
            }
            bonus, learning_reasons = learning_bonus(job, hypotheses)
            if bonus:
                job.triage_score = round(max(0.0, min(100.0, job.triage_score + bonus)), 1)
                job.triage_reasons.extend(learning_reasons)
                job.provider_meta["learning_bonus"] = bonus
        all_jobs.extend(ranked)

    best: dict[str, Job] = {}
    for job in all_jobs:
        key = job.url or job.id
        if key not in best or job.triage_score > best[key].triage_score:
            best[key] = job

    limit = args.limit or runtime["max_total"]
    ranked = sorted(best.values(), key=lambda j: -j.triage_score)[:limit]
    vault = merge_job_vault(ctx["paths"]["job_vault"], ranked)

    maps_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if maps_key:
        geocoder = GooglePlacesGeocoder(maps_key)
        vault = geotag_vault(
            vault,
            geocoder,
            region_code=runtime["country"],
            only_missing=True,
            country_enricher=enrich_country_matrix,
        )
        write_json(ctx["paths"]["job_vault"], vault)
        map_root = ctx["root"] / "data/maps"
        map_root.mkdir(parents=True, exist_ok=True)
        for name, zoom in [("world", 3), ("country", 5), ("region", 8), ("city", 12)]:
            (map_root / f"{name}.json").write_text(
                json.dumps(build_map_payload(vault.get("jobs", []), zoom), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    _render_all(ctx, ranked, lane=args.lane)
    print(json.dumps({
        "jobs": len(ranked),
        "jobs_ever_seen": vault.get("total_jobs_ever_seen", len(ranked)),
        "geotagging": bool(maps_key),
        "search_overlay_used": bool(overlay),
        "learning_event_count": len(outcome_events),
    }, ensure_ascii=False, indent=2))


def cmd_drill(args):
    manifest = _manifest(args.manifest)
    ctx = _load_context(manifest)
    root = ctx["root"]
    outdir = Path(args.out)
    if not outdir.is_absolute():
        outdir = root / outdir
    outdir.mkdir(parents=True, exist_ok=True)

    supplied_text = args.text or ""
    if args.text_file:
        supplied_text = Path(args.text_file).read_text(encoding="utf-8")
    job = fetch_public_job(args.url, supplied_text=supplied_text)
    if args.title and not job.title:
        job.title = args.title
    if args.company and not job.company:
        job.company = args.company
    if args.deadline and not job.deadline:
        job.deadline = args.deadline
    job.lane = args.lane

    packet = build_packet(
        job,
        ctx["profile"],
        args.lane,
        run_counter_path=root / "data/hrdm_runseq.json",
        hy_filter_decision=args.hy_filter or None,
    )
    (outdir / "job.json").write_text(json.dumps(job.full_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (outdir / "HRDM_input_packet.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (outdir / "HRDM_prompt.md").write_text(packet_prompt(packet), encoding="utf-8")

    schema_path = CENTRAL_ROOT / "core/hrdm/hrdm_result.schema.json"
    hrdm = run_ai_hrdm(packet, schema_path) or fallback_hrdm(packet)
    (outdir / "HRDM_result.json").write_text(json.dumps(hrdm, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report_entry = save_report_bundle(root, hrdm, ctx["paths"]["hrdm_ledger"])

    ai_app = run_ai_application(job.full_dict(), ctx["profile"], hrdm, args.lane)
    app = ai_app or fallback_application(job.full_dict(), ctx["profile"], hrdm)
    app_json = outdir / "application_package.json"
    app_json.write_text(json.dumps(app, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    app_doc = write_application_docx(outdir, job.full_dict(), ctx["profile"], app)

    ai_hrdm_used = hrdm.get("ai_status") != "not_run"
    external_use_allowed = bool(ai_hrdm_used and ai_app is not None)
    if int(args.issue_number or 0) > 0:
        bind_analysis(
            ctx["paths"]["applications"],
            int(args.issue_number),
            packet["process_id"],
            external_use_allowed=external_use_allowed,
            report_paths=report_entry["paths"],
            application_paths={
                "json": str(app_json.relative_to(root)),
                "docx": str(app_doc.relative_to(root)),
            },
        )

    maintain_hrdm_reports(root, ctx["paths"]["hrdm_ledger"], control_room=None)
    _render_all(ctx)

    print(json.dumps({
        "process_id": packet["process_id"],
        "application_docx": str(app_doc),
        "hrdm_report": report_entry["paths"],
        "hy_filter": (hrdm.get("hybridianesque") or {}).get("status"),
        "ai_used": ai_hrdm_used,
        "application_ai_used": ai_app is not None,
        "external_use_allowed": external_use_allowed,
    }, ensure_ascii=False, indent=2))


def cmd_track(args):
    ctx = _load_context(_manifest(args.manifest))
    cases_path = ctx["paths"]["applications"]
    if args.action == "choose":
        job = Job.from_dict(json.loads(Path(args.job_json).read_text(encoding="utf-8")))
        case = choose_case(cases_path, job, args.issue_number, args.issue_url, args.priority)
        if not args.analysis_complete:
            case["status"] = "preparing"
            case["external_use_allowed"] = False
            case["next_action"] = "Complete and validate HRDM before external use"
            data = load_cases(cases_path)
            for row in data.get("cases", []):
                if row.get("issue_number") == args.issue_number:
                    row.update(case)
            write_json(cases_path, data)
    elif args.action == "status":
        case = update_case(cases_path, args.issue_number, args.status, args.date, args.next_action, args.next_action_date)
    elif args.action == "priority":
        case = update_priority(cases_path, args.issue_number, args.priority)
    elif args.action == "event":
        case = append_case_event(
            cases_path,
            args.issue_number,
            args.event_type,
            source=args.event_source,
            note=args.note,
            at=args.date,
        )
    else:
        raise SystemExit(f"Unsupported action: {args.action}")

    _render_all(ctx)
    print(json.dumps(case, ensure_ascii=False, indent=2))


def cmd_render(args):
    ctx = _load_context(_manifest(args.manifest))
    _render_all(ctx)
    print("CareerHub surfaces rendered.")


def cmd_maintain(args):
    ctx = _load_context(_manifest(args.manifest))
    archived = maintain_hrdm_reports(
        ctx["root"],
        ctx["paths"]["hrdm_ledger"],
        control_room=ctx["root"] / "CONTROL_ROOM.md",
    )
    print(json.dumps({"archived_hrdm_reports": archived}, indent=2))


def build_parser():
    parser = argparse.ArgumentParser(prog="careerhub")
    parser.add_argument("--manifest", required=True, help="Path to stable careerhub.yaml profile manifest")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate")
    validate.set_defaults(func=cmd_validate)

    scan = sub.add_parser("scan")
    scan.add_argument("--lane", default="all")
    scan.add_argument("--limit", type=int, default=0)
    scan.add_argument("--search-overlay", default="")
    scan.set_defaults(func=cmd_scan)

    drill = sub.add_parser("drill")
    drill.add_argument("--url", required=True)
    drill.add_argument("--text", default="")
    drill.add_argument("--text-file", default="")
    drill.add_argument("--title", default="")
    drill.add_argument("--company", default="")
    drill.add_argument("--deadline", default="")
    drill.add_argument("--lane", choices=["core", "adjacent", "bridge"], default="core")
    drill.add_argument("--hy-filter", choices=["Yes", "No"], default="")
    drill.add_argument("--out", default="output")
    drill.add_argument("--issue-number", type=int, default=0)
    drill.set_defaults(func=cmd_drill)

    track = sub.add_parser("track")
    track.add_argument("--action", choices=["choose", "status", "priority", "event"], required=True)
    track.add_argument("--job-json", default="")
    track.add_argument("--issue-number", type=int, required=True)
    track.add_argument("--issue-url", default="")
    track.add_argument("--priority", type=int, default=3)
    track.add_argument("--status", default="")
    track.add_argument("--date", default="")
    track.add_argument("--next-action", default="")
    track.add_argument("--next-action-date", default="")
    track.add_argument("--analysis-complete", action="store_true")
    track.add_argument("--event-type", default="")
    track.add_argument("--event-source", choices=["user", "system", "employer"], default="user")
    track.add_argument("--note", default="")
    track.set_defaults(func=cmd_track)

    render = sub.add_parser("render")
    render.set_defaults(func=cmd_render)

    maintain = sub.add_parser("maintain")
    maintain.set_defaults(func=cmd_maintain)

    return parser


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
