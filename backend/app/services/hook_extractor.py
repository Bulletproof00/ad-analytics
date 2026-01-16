import hashlib
import re
from typing import Iterable


def normalize_hook(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _first_body(copy_bodies: dict | list | None) -> str | None:
    if not copy_bodies:
        return None
    if isinstance(copy_bodies, list):
        return str(copy_bodies[0]) if copy_bodies else None
    if isinstance(copy_bodies, dict):
        values = list(copy_bodies.values())
        return str(values[0]) if values else None
    return None


def extract_hook(copy_bodies: dict | list | None) -> str | None:
    first = _first_body(copy_bodies)
    if not first:
        return None
    split = re.split(r"[.!?\n]", first)
    hook = split[0][:120].strip()
    return hook or None


def hook_hash(hook: str) -> str:
    normalized = normalize_hook(hook)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def collect_hooks(copy_bodies: dict | list | None) -> tuple[str | None, str | None]:
    hook = extract_hook(copy_bodies)
    if not hook:
        return None, None
    return hook, hook_hash(hook)


def hook_preview(copy_bodies: dict | list | None) -> str | None:
    return extract_hook(copy_bodies)
