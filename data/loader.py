from dataclasses import dataclass, field
from pathlib import Path

import yaml

CASES_FILE = Path(__file__).parent / "cases.yaml"


@dataclass
class Case:
    id: str
    featured: bool
    category: str
    title: str
    client: str
    product: str
    tasks: list[str] = field(default_factory=list)
    result: str = ""
    review: str | None = None
    detailed_case: str | None = None
    images: list[str] = field(default_factory=list)
    links: dict[str, str] = field(default_factory=dict)


def _load_raw() -> list[dict]:
    with CASES_FILE.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or []


_CASES: dict[str, Case] = {}
_ORDER: list[str] = []


def _ensure_loaded() -> None:
    if _CASES:
        return
    for raw in _load_raw():
        case = Case(
            id=raw["id"],
            featured=raw.get("featured", False),
            category=raw.get("category", ""),
            title=raw["title"],
            client=raw.get("client", ""),
            product=raw.get("product", ""),
            tasks=raw.get("tasks") or [],
            result=raw.get("result", ""),
            review=raw.get("review"),
            detailed_case=raw.get("detailed_case"),
            images=raw.get("images") or [],
            links=raw.get("links") or {},
        )
        _CASES[case.id] = case
        _ORDER.append(case.id)


def all_cases() -> list[Case]:
    _ensure_loaded()
    return [_CASES[cid] for cid in _ORDER]


def featured_cases() -> list[Case]:
    return [c for c in all_cases() if c.featured]


def other_cases() -> list[Case]:
    return [c for c in all_cases() if not c.featured]


def get_case(case_id: str) -> Case | None:
    _ensure_loaded()
    return _CASES.get(case_id)
