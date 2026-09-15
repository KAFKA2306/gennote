import hashlib
import json
from pathlib import Path
from typing import Callable


def publication_id(article: str) -> str:
    return hashlib.sha256(article.encode("utf-8")).hexdigest()


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def publish_once(article: str, state_path: Path, create: Callable[[str], object]) -> dict:
    identity = publication_id(article)
    state = _load(state_path)
    previous = state.get(identity)
    if previous and previous.get("status") in {"confirmed", "uncertain"}:
        return previous

    # Persist the in-flight boundary before the remote side effect. If the process
    # dies after the remote create, the next run fails closed instead of duplicating it.
    state[identity] = {"status": "uncertain", "publication_id": identity}
    _save(state_path, state)

    try:
        response = create(article)
    except Exception as exc:
        result = {
            "status": "uncertain",
            "publication_id": identity,
            "error": type(exc).__name__,
        }
        state[identity] = result
        _save(state_path, state)
        return result

    location = response.headers.get("Location") if getattr(response, "headers", None) else None
    if getattr(response, "status_code", None) == 201 and location and location.startswith(("http://", "https://")):
        result = {
            "status": "confirmed",
            "publication_id": identity,
            "remote_url": location,
        }
    else:
        result = {
            "status": "uncertain",
            "publication_id": identity,
            "http_status": getattr(response, "status_code", None),
        }

    state[identity] = result
    _save(state_path, state)
    return result
