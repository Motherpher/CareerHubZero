#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import requests

SOURCE_URL = "https://www.scb.se/contentassets/80b5648961b647379bf147e791aa446b/lokala-arbetsmarknader-20202024-bas.xlsx"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
DOC_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def _shared_strings(zf: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    out = []
    for si in root.findall("m:si", NS):
        out.append("".join(t.text or "" for t in si.iterfind(".//m:t", NS)))
    return out


def _sheet_files(zf: zipfile.ZipFile) -> list[tuple[str, str]]:
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    relmap = {r.attrib["Id"]: r.attrib["Target"] for r in rels.findall("r:Relationship", REL_NS)}
    out = []
    for sheet in wb.find("m:sheets", NS):
        name = sheet.attrib.get("name", "")
        rid = sheet.attrib.get(f"{{{DOC_REL}}}id")
        target = relmap.get(rid or "", "")
        if target and not target.startswith("/"):
            target = "xl/" + target.lstrip("/")
        out.append((name, target))
    return out


def _cell_value(cell: ET.Element, shared: list[str]) -> str:
    typ = cell.attrib.get("t")
    if typ == "inlineStr":
        return "".join(t.text or "" for t in cell.iterfind(".//m:t", NS)).strip()
    node = cell.find("m:v", NS)
    raw = (node.text or "").strip() if node is not None else ""
    if typ == "s" and raw:
        try:
            return shared[int(raw)].strip()
        except Exception:
            return raw
    return raw


def _rows(zf: zipfile.ZipFile, path: str, shared: list[str]) -> list[list[str]]:
    root = ET.fromstring(zf.read(path))
    out = []
    for row in root.iterfind(".//m:sheetData/m:row", NS):
        values = [_cell_value(cell, shared) for cell in row.findall("m:c", NS)]
        if any(values):
            out.append(values)
    return out


def _record(values: list[str], sheet_name: str) -> dict | None:
    cleaned = [str(x).strip() for x in values]
    la_idx = next((i for i, x in enumerate(cleaned) if re.fullmatch(r"LA\d{4,}", x, re.I)), None)
    if la_idx is None:
        return None

    municipality_candidates = [
        (i, x) for i, x in enumerate(cleaned)
        if re.fullmatch(r"\d{4}", x) and not re.fullmatch(r"20(?:20|21|22|23|24)", x)
    ]
    if not municipality_candidates:
        return None
    municipality_idx, municipality_code = municipality_candidates[-1]

    year_match = re.search(r"20(?:20|21|22|23|24)", sheet_name)
    if not year_match:
        year_match = next((re.search(r"20(?:20|21|22|23|24)", x) for x in cleaned if re.search(r"20(?:20|21|22|23|24)", x)), None)
    year = int(year_match.group(0)) if year_match else None

    def after(idx: int) -> str:
        for value in cleaned[idx + 1:]:
            if value and not re.fullmatch(r"\d+(?:\.\d+)?", value) and not re.fullmatch(r"LA\d+", value, re.I):
                return value
        return ""

    return {
        "year": year,
        "la_code": cleaned[la_idx].upper(),
        "la_name": after(la_idx),
        "municipality_code": municipality_code,
        "municipality_name": after(municipality_idx),
    }


def parse_xlsx(blob: bytes) -> dict:
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        shared = _shared_strings(zf)
        records = []
        sheet_debug = []
        for sheet_name, path in _sheet_files(zf):
            if not path:
                continue
            rows_here = _rows(zf, path, shared)
            sheet_records = []
            for values in rows_here:
                rec = _record(values, sheet_name)
                if rec:
                    records.append(rec)
                    sheet_records.append(rec)
            sheet_debug.append({
                "sheet": sheet_name,
                "row_count": len(rows_here),
                "candidate_records": len(sheet_records),
                "sample_rows": rows_here[:8],
                "sample_records": sheet_records[:5],
            })

    years = sorted({r["year"] for r in records if r["year"]})
    if not years:
        raise RuntimeError("No LA year could be detected in SCB workbook.")
    latest = years[-1]
    latest_rows = [r for r in records if r["year"] == latest]
    by_municipality = {}
    for row in latest_rows:
        by_municipality[row["municipality_code"]] = row
    rows = sorted(by_municipality.values(), key=lambda x: x["municipality_code"])
    if len(rows) != 290:
        print("SCB_PARSE_DIAGNOSTIC", json.dumps({
            "years": years,
            "latest": latest,
            "all_records": len(records),
            "latest_records": len(latest_rows),
            "unique_municipalities": len(rows),
            "sample_latest": latest_rows[:20],
            "sheets": sheet_debug,
        }, ensure_ascii=False))
        raise RuntimeError(f"Expected 290 municipality assignments for LA {latest}, found {len(rows)}.")
    return {
        "schema_version": "1.0",
        "reference_year": latest,
        "source": "SCB BAS — Lokala arbetsmarknader år 2020–2024",
        "source_url": SOURCE_URL,
        "municipality_count": len(rows),
        "labour_market_count": len({r["la_code"] for r in rows}),
        "records": rows,
    }


def main() -> int:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/geography/sweden_local_labour_markets.json")
    response = requests.get(SOURCE_URL, timeout=60)
    response.raise_for_status()
    payload = parse_xlsx(response.content)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "reference_year": payload["reference_year"],
        "municipalities": payload["municipality_count"],
        "labour_markets": payload["labour_market_count"],
        "output": str(out),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
