#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dateutil import parser as dtparser

MILESTONES = {7, 3, 1, 0}
TERMINAL = {"offer", "denied", "withdrawn", "archived"}


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: dict):
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def days_left(value: str) -> int | None:
    if not value:
        return None
    try:
        d = dtparser.parse(str(value))
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return (d.date() - datetime.now(timezone.utc).date()).days
    except Exception:
        return None


def github_comment(repo: str, issue: int, token: str, message: str) -> bool:
    if not token or not repo or not issue:
        return False
    r = requests.post(
        f"https://api.github.com/repos/{repo}/issues/{issue}/comments",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={"body": message},
        timeout=20,
    )
    return r.ok


def email_send(subject: str, text: str) -> bool:
    key = os.getenv("RESEND_API_KEY", "")
    to = os.getenv("CAREERHUB_NOTIFY_EMAIL", "")
    sender = os.getenv("CAREERHUB_NOTIFY_EMAIL_FROM", "")
    if not key or not to or not sender:
        return False
    r = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"from": sender, "to": [to], "subject": subject, "text": text},
        timeout=20,
    )
    return r.ok


def sms_send(text: str) -> bool:
    sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    token = os.getenv("TWILIO_AUTH_TOKEN", "")
    from_number = os.getenv("TWILIO_FROM_NUMBER", "")
    to = os.getenv("CAREERHUB_NOTIFY_PHONE", "")
    if not all([sid, token, from_number, to]):
        return False
    r = requests.post(
        f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
        auth=(sid, token),
        data={"From": from_number, "To": to, "Body": text},
        timeout=20,
    )
    return r.ok


def existing_channels(case: dict, key: str) -> set[str]:
    channels = set()
    for row in case.get("notification_log", []):
        if isinstance(row, dict) and row.get("key") == key:
            channels.update(row.get("channels", []))
    return channels


def main():
    path = Path(os.getenv("CAREERHUB_APPLICATIONS", "CareerHub/data/applications.json"))
    if not path.exists():
        print("No applications file; nothing to notify.")
        return

    data = read(path)
    repo = os.getenv("GITHUB_REPOSITORY", "")
    gh_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN", "")
    changed = False

    for case in data.get("cases", []):
        if case.get("status") in TERMINAL:
            continue
        days = days_left(case.get("deadline", ""))
        if days not in MILESTONES:
            continue

        deadline = str(case.get("deadline") or "")[:10]
        key = f"deadline:{deadline}:{days}"
        already = existing_channels(case, key)
        issue = int(case.get("issue_number") or 0)
        role = case.get("title") or "job"
        employer = case.get("company") or ""
        day_text = "today" if days == 0 else f"in {days} day" if days == 1 else f"in {days} days"
        subject = f"Karriärhubben – sista ansökningsdag: {role} — {day_text}"
        text = f"{role} at {employer}: sista ansökningsdag är {day_text} ({deadline})."
        if case.get("issue_url"):
            text += f" Case: {case['issue_url']}"

        sent = []
        if "github" not in already:
            message = (
                f"## Påminnelse om sista ansökningsdag\n\n"
                f"**{role} — {employer}** har sista ansökningsdag **{day_text}** ({deadline}).\n\n"
                f"Nuvarande läge: **{case.get('status','')}**."
            )
            if github_comment(repo, issue, gh_token, message):
                sent.append("github")

        email_configured = bool(os.getenv("RESEND_API_KEY") and os.getenv("CAREERHUB_NOTIFY_EMAIL") and os.getenv("CAREERHUB_NOTIFY_EMAIL_FROM"))
        if email_configured and "email" not in already and email_send(subject, text):
            sent.append("email")

        sms_configured = bool(
            os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN")
            and os.getenv("TWILIO_FROM_NUMBER") and os.getenv("CAREERHUB_NOTIFY_PHONE")
        )
        if sms_configured and "sms" not in already and sms_send(text):
            sent.append("sms")

        if sent:
            case.setdefault("notification_log", []).append({
                "key": key,
                "at": datetime.now(timezone.utc).isoformat(),
                "days_left": days,
                "channels": sent,
            })
            changed = True
            print(f"Reminder sent for case #{issue}: {', '.join(sent)}")

    if changed:
        write(path, data)
    else:
        print("No new reminders due.")


if __name__ == "__main__":
    main()
