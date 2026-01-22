# TEST/conftest.py
"""
Centralized pytest config for exist-fdsn-station.

URL split:
  --scheme        (default: http)
  --host          (host[:port], default: localhost:80)
  --base-path     (default: /fdsnws/station/1)

INPUT normalization (PUT/POST payloads):
  --in-z-mode            as-is | add-z | drop-z
  --in-fraction-mode     as-is | strip

OUTPUT normalization (golden before compare) with per-type overrides:
  Global defaults:
    --golden-z-mode            as-is | add-z | drop-z
    --golden-fraction-mode     as-is | strip
  Type overrides (optional; fall back to globals if omitted):
    --golden-text-z-mode            as-is | add-z | drop-z
    --golden-text-fraction-mode     as-is | strip
    --golden-json-z-mode            as-is | add-z | drop-z
    --golden-json-fraction-mode     as-is | strip
    --golden-xml-z-mode             as-is | add-z | drop-z
    --golden-xml-fraction-mode      as-is | strip

Legacy switches (Z only; leave fractions independent):
  --disable-text-z-normalize
  --disable-json-z-normalize

Diagnostics:
  --json-diff
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Tuple

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass(frozen=True)
class Cfg:
    scheme: str
    host: str
    base_path: str
    provider: str
    data_dir: Path
    timeout_s: int
    retries: int
    update_snapshots: bool
    default_auth: Tuple[str, str]

    # INPUT (request payload)
    in_z_mode: str                   # as-is | add-z | drop-z
    in_fraction_mode: str            # as-is | strip

    # OUTPUT (goldens) global defaults
    golden_z_mode: str               # as-is | add-z | drop-z
    golden_fraction_mode: str        # as-is | strip

    # OUTPUT per-type overrides (None => use global)
    golden_text_z_mode: str | None
    golden_text_fraction_mode: str | None
    golden_json_z_mode: str | None
    golden_json_fraction_mode: str | None
    golden_xml_z_mode: str | None
    golden_xml_fraction_mode: str | None

    # Legacy Z-only disable flags (do not affect fraction)
    golden_text_z_disable: bool
    golden_json_z_disable: bool

    # Diagnostics
    json_diff: bool


def _vc(opt: str, val: str, allowed: tuple[str, ...]) -> str:
    v = (val or "").lower()
    if v not in allowed:
        raise pytest.UsageError(f"{opt} must be one of: {', '.join(allowed)}")
    return v


def pytest_addoption(parser: pytest.Parser) -> None:
    g = parser.getgroup("exist-fdsn-station")
    g.addoption("--scheme", action="store", default="http")
    g.addoption("--host", action="store", default="localhost:80", help="service host[:port]")
    g.addoption("--base-path", action="store", default="/fdsnws/station/1")
    g.addoption("--provider", action="store", default="")
    g.addoption("--data-dir", action="store", default="TEST/data")
    g.addoption("--timeout", action="store", type=int, default=20)
    g.addoption("--retries", action="store", type=int, default=2)
    g.addoption("--auth-user", action="store", default="")
    g.addoption("--auth-pass", action="store", default="")
    g.addoption("--update-snapshots", action="store_true", default=False)

    # INPUT
    g.addoption("--in-z-mode", action="store", default="as-is",
                help="INPUT payload: as-is|add-z|drop-z")
    g.addoption("--in-fraction-mode", action="store", default="as-is",
                help="INPUT payload: as-is|strip")

    # OUTPUT global
    g.addoption("--golden-z-mode", action="store", default="as-is",
                help="GOLDEN default: as-is|add-z|drop-z")
    g.addoption("--golden-fraction-mode", action="store", default="as-is",
                help="GOLDEN default: as-is|strip")

    # OUTPUT per-type overrides (optional)
    g.addoption("--golden-text-z-mode", action="store", default=None)
    g.addoption("--golden-text-fraction-mode", action="store", default=None)
    g.addoption("--golden-json-z-mode", action="store", default=None)
    g.addoption("--golden-json-fraction-mode", action="store", default=None)
    g.addoption("--golden-xml-z-mode", action="store", default=None)
    g.addoption("--golden-xml-fraction-mode", action="store", default=None)

    # Legacy Z-only disables
    g.addoption("--disable-text-z-normalize", action="store_true", default=False)
    g.addoption("--disable-json-z-normalize", action="store_true", default=False)

    # Diagnostics
    g.addoption("--json-diff", action="store_true", default=False,
                help="Show unified diff for JSON mismatches.")


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "smoke: fast checks (version/PUT/DELETE)")
    config.addinivalue_line("markers", "integration: migrated legacy cases (non-management)")
    config.addinivalue_line("markers", "management: migrated management cases (run last)")


@pytest.fixture(scope="session")
def cfg(request: pytest.FixtureRequest) -> Cfg:
    o = request.config
    auth_user = (o.getoption("--auth-user") or "").strip()
    auth_pass = (o.getoption("--auth-pass") or "").strip()
    default_auth: Tuple[str, str] = (auth_user, auth_pass) if (auth_user or auth_pass) else ("fdsn", "fdsn")

    base_path = str(o.getoption("--base-path") or "/fdsnws/station/1")
    if not base_path.startswith("/"):
        base_path = "/" + base_path

    # INPUT
    in_z_mode = _vc("--in-z-mode", o.getoption("--in-z-mode"), ("as-is", "add-z", "drop-z"))
    in_fraction_mode = _vc("--in-fraction-mode", o.getoption("--in-fraction-mode"), ("as-is", "strip"))

    # OUTPUT globals
    golden_z_mode = _vc("--golden-z-mode", o.getoption("--golden-z-mode"), ("as-is", "add-z", "drop-z"))
    golden_fraction_mode = _vc("--golden-fraction-mode", o.getoption("--golden-fraction-mode"), ("as-is", "strip"))

    # OUTPUT per-type overrides (validate only if provided)
    def _opt_mode(name: str, allowed: tuple[str, ...]):
        val = o.getoption(name)
        if val is None:
            return None
        return _vc(name, val, allowed)

    text_z = _opt_mode("--golden-text-z-mode", ("as-is", "add-z", "drop-z"))
    text_f = _opt_mode("--golden-text-fraction-mode", ("as-is", "strip"))
    json_z = _opt_mode("--golden-json-z-mode", ("as-is", "add-z", "drop-z"))
    json_f = _opt_mode("--golden-json-fraction-mode", ("as-is", "strip"))
    xml_z  = _opt_mode("--golden-xml-z-mode", ("as-is", "add-z", "drop-z"))
    xml_f  = _opt_mode("--golden-xml-fraction-mode", ("as-is", "strip"))

    # Legacy Z-only disables
    text_z_disable = bool(o.getoption("--disable-text-z-normalize"))
    json_z_disable = bool(o.getoption("--disable-json-z-normalize"))

    return Cfg(
        scheme=str(o.getoption("--scheme") or "http"),
        host=str(o.getoption("--host") or "localhost:80"),
        base_path=base_path,
        provider=str(o.getoption("--provider") or ""),
        data_dir=Path(o.getoption("--data-dir")).resolve(),
        timeout_s=int(o.getoption("--timeout")),
        retries=int(o.getoption("--retries")),
        update_snapshots=bool(o.getoption("--update-snapshots")),
        default_auth=default_auth,
        in_z_mode=in_z_mode,
        in_fraction_mode=in_fraction_mode,
        golden_z_mode=golden_z_mode,
        golden_fraction_mode=golden_fraction_mode,
        golden_text_z_mode=text_z,
        golden_text_fraction_mode=text_f,
        golden_json_z_mode=json_z,
        golden_json_fraction_mode=json_f,
        golden_xml_z_mode=xml_z,
        golden_xml_fraction_mode=xml_f,
        golden_text_z_disable=text_z_disable,
        golden_json_z_disable=json_z_disable,
        json_diff=bool(o.getoption("--json-diff")),
    )


@pytest.fixture(scope="session")
def expected_dir() -> Path:
    p = Path("TEST/expected")
    p.mkdir(parents=True, exist_ok=True)
    return p


def _make_session(retries: int) -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=retries, read=retries, connect=retries, status=retries,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "POST", "PUT", "DELETE"]),
        backoff_factor=0.3, raise_on_status=False,
    )
    a = HTTPAdapter(max_retries=retry, pool_maxsize=16)
    s.mount("http://", a)
    s.mount("https://", a)
    return s


@pytest.fixture(scope="session")
def http(cfg: Cfg) -> Generator[requests.Session, None, None]:
    s = _make_session(cfg.retries)
    try:
        yield s
    finally:
        s.close()


@pytest.fixture
def host(request):
    return request.config.getoption("--host")
