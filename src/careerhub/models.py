from __future__ import annotations

from dataclasses import dataclass, field, asdict
from hashlib import sha1
from typing import Any
import re


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    if any(marker in text for marker in ["Ã", "Â", "Ø", "Ù", "â"]):
        try:
            repaired = text.encode("latin1").decode("utf-8")
            if repaired.count("�") <= text.count("�"):
                text = repaired
        except Exception:
            pass
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@dataclass
class Job:
    source: str
    title: str
    company: str = ""
    location: str = ""
    employment_type: str = ""
    work_mode: str = ""
    published: str = ""
    deadline: str = ""
    url: str = ""
    salary: str = ""
    description: str = ""
    provider_id: str = ""
    lane: str = ""
    matched_query: str = ""
    triage_score: float = 0.0
    triage_reasons: list[str] = field(default_factory=list)
    review_flags: list[str] = field(default_factory=list)
    provider_meta: dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        basis = self.url or f"{self.source}|{self.company}|{self.title}|{self.location}|{self.provider_id}"
        return sha1(basis.encode("utf-8")).hexdigest()[:16]

    @property
    def search_blob(self) -> str:
        values = [
            self.title, self.company, self.location, self.employment_type,
            self.work_mode, self.description
        ]
        return clean_text(" ".join(clean_text(v) for v in values)).lower()

    def public_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["id"] = self.id
        data["description_excerpt"] = clean_text(self.description)[:700]
        data.pop("description", None)
        data.pop("provider_meta", None)
        return data

    def full_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["id"] = self.id
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Job":
        allowed = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in allowed})
