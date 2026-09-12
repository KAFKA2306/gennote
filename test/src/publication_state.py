from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Callable, Protocol
from urllib.parse import urlparse


class ResponseLike(Protocol):
    status_code: int
    headers: dict[str, str]


@dataclass(frozen=True)
class PublicationEvidence:
    publication_id: str
    status: str
    remote_url: str | None = None
    reason: str | None = None

    @property
    def confirmed(self) -> bool:
        return self.status == "confirmed"


def publication_identity(title: str, content: str) -> str:
    payload = json.dumps(
        {"title": title, "content": content},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _state_path(state_dir: Path, publication_id: str) -> Path:
    return state_dir / f"{publication_id}.json"


def _read_evidence(state_dir: Path, publication_id: str) -> PublicationEvidence | None:
    path = _state_path(state_dir, publication_id)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("publication_id") != publication_id:
        raise ValueError(f"publication state identity mismatch: {path}")
    return PublicationEvidence(
        publication_id=publication_id,
        status=data["status"],
        remote_url=data.get("remote_url"),
        reason=data.get("reason"),
    )


def _write_evidence(state_dir: Path, evidence: PublicationEvidence) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    path = _state_path(state_dir, evidence.publication_id)
    tmp_path = path.with_suffix(f"{path.suffix}.tmp")
    tmp_path.write_text(
        json.dumps(asdict(evidence), ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(tmp_path, path)


def _usable_remote_url(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return value


def publish_once(
    *,
    publication_id: str,
    state_dir: Path,
    create: Callable[[], ResponseLike],
) -> PublicationEvidence:
    existing = _read_evidence(state_dir, publication_id)
    if existing is not None and existing.status in {"confirmed", "uncertain"}:
        return existing

    # Persist uncertainty before the external side effect. If the process dies after
    # the remote create, a rerun will stop instead of issuing a duplicate POST.
    in_flight = PublicationEvidence(
        publication_id=publication_id,
        status="uncertain",
        reason="create_in_flight",
    )
    _write_evidence(state_dir, in_flight)

    try:
        response = create()
    except Exception as exc:
        uncertain = PublicationEvidence(
            publication_id=publication_id,
            status="uncertain",
            reason=f"request_exception:{type(exc).__name__}",
        )
        _write_evidence(state_dir, uncertain)
        return uncertain

    if response.status_code == 201:
        remote_url = _usable_remote_url(response.headers.get("Location"))
        if remote_url is None:
            uncertain = PublicationEvidence(
                publication_id=publication_id,
                status="uncertain",
                reason="created_without_remote_identity",
            )
            _write_evidence(state_dir, uncertain)
            return uncertain
        confirmed = PublicationEvidence(
            publication_id=publication_id,
            status="confirmed",
            remote_url=remote_url,
        )
        _write_evidence(state_dir, confirmed)
        return confirmed

    failed = PublicationEvidence(
        publication_id=publication_id,
        status="failed",
        reason=f"http_status:{response.status_code}",
    )
    _write_evidence(state_dir, failed)
    return failed


def confirm_from_readback(
    *, publication_id: str, state_dir: Path, remote_url: str
) -> PublicationEvidence:
    existing = _read_evidence(state_dir, publication_id)
    if existing is None or existing.status != "uncertain":
        raise ValueError("only an uncertain publication can be resolved by read-back")
    usable_url = _usable_remote_url(remote_url)
    if usable_url is None:
        raise ValueError("read-back remote URL is not usable")
    confirmed = PublicationEvidence(
        publication_id=publication_id,
        status="confirmed",
        remote_url=usable_url,
        reason="confirmed_by_readback",
    )
    _write_evidence(state_dir, confirmed)
    return confirmed
