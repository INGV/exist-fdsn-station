# TEST/test_cases.py
"""
Mapping-driven tests (YAML/JSON/CSV).

Independence of normalization:
- INPUT (PUT/POST): cfg.in_fraction_mode and cfg.in_z_mode are applied independently.
- OUTPUT (goldens before compare): fraction and Z are applied independently,
  with per-type modes (XML/JSON/TEXT) that fall back to global golden modes.
  Legacy --disable-*-z-normalize only forces Z mode to 'as-is' for that type;
  it does not affect fraction mode.

Other behavior unchanged.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable, Tuple
import re, glob, csv, json, difflib
from pathlib import Path
from urllib.parse import urlunsplit

import pytest
import requests

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

try:
    from lxml import etree
except Exception:
    etree = None

try:
    from TEST.main import diff_texts
except Exception:
    def diff_texts(a, b, fromfile="expected", tofile="actual", n: int = 60) -> str:
        import difflib
        if isinstance(a, (bytes, bytearray)): a = a.decode("utf-8", errors="replace")
        if isinstance(b, (bytes, bytearray)): b = b.decode("utf-8", errors="replace")
        return "\n".join(difflib.unified_diff(a.splitlines(), b.splitlines(), fromfile=fromfile, tofile=tofile, n=n))

EXPECTED_DIR = Path("TEST/expected")
MGMT_DEFAULT_PATH = "/exist/apps/fdsn-station/management/network?"

# ---------------- Small utils ----------------

def _join_paths(a: str, b: str) -> str:
    if not a.endswith("/"): a = a + "/"
    if b.startswith("/"): b = b[1:]
    return a + b

def build_url(cfg, path: str) -> str:
    if path.startswith("/exist") or path.startswith("/fdsnws"):
        full_path = path
    else:
        full_path = _join_paths(cfg.base_path, path)
    return urlunsplit((cfg.scheme, cfg.host, full_path, "", ""))

def read_bytes(path: str) -> bytes:
    return Path(path).read_bytes()

def _normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

# ---------------- Timestamp normalization ----------------
# Match: YYYY-MM-DDTHH:mm:ss(.sss...)?(Z)?
_TS_RE = re.compile(
    r"\b("
    r"\d{4}-\d{2}-\d{2}T"
    r"\d{2}:\d{2}:\d{2}"
    r")(\.\d+)?(Z)?\b"
)

def normalize_trailing_z(text: str, mode: str) -> str:
    if mode == "as-is": return text
    def repl(m: re.Match[str]) -> str:
        core = m.group(1)
        frac = m.group(2) or ""
        if mode == "add-z":  return f"{core}{frac}Z"
        if mode == "drop-z": return f"{core}{frac}"
        return f"{core}{frac}{'Z' if m.group(3) else ''}"
    return _TS_RE.sub(repl, text)

def normalize_fractional_seconds(text: str, mode: str) -> str:
    if mode == "as-is": return text
    def repl(m: re.Match[str]) -> str:
        core = m.group(1)
        frac = m.group(2)  # like ".0001200" or None
        z    = m.group(3) or ""
        if not frac: return f"{core}{z}"
        digits = re.sub(r"0+$", "", frac[1:])
        return (f"{core}.{digits}{z}") if digits else f"{core}{z}"
    return _TS_RE.sub(repl, text)

def _apply_modes(text: str, z_mode: str, frac_mode: str) -> str:
    # Fraction then Z to preserve intent
    text = normalize_fractional_seconds(text, frac_mode)
    text = normalize_trailing_z(text, z_mode)
    return text

# Helper to pick per-type OUTPUT modes with fallbacks and legacy Z-disables
def _output_modes_for(cfg, kind: str) -> tuple[str, str]:
    # kind in {"text","json","xml"}
    # Start from globals
    z_mode = getattr(cfg, "golden_z_mode", "as-is")
    f_mode = getattr(cfg, "golden_fraction_mode", "as-is")
    # Overrides
    if kind == "text":
        z_mode = (cfg.golden_text_z_mode or z_mode)
        f_mode = (cfg.golden_text_fraction_mode or f_mode)
        if getattr(cfg, "golden_text_z_disable", False):
            z_mode = "as-is"
    elif kind == "json":
        z_mode = (cfg.golden_json_z_mode or z_mode)
        f_mode = (cfg.golden_json_fraction_mode or f_mode)
        if getattr(cfg, "golden_json_z_disable", False):
            z_mode = "as-is"
    elif kind == "xml":
        z_mode = (cfg.golden_xml_z_mode  or z_mode)
        f_mode = (cfg.golden_xml_fraction_mode or f_mode)
    return z_mode, f_mode

# ---------------- Attach/transform helpers ----------------

def _attach_query(path: str, raw_query: str) -> str:
    if not raw_query: return path
    sep = "&" if "?" in path else "?"
    return f"{path}{sep}{raw_query}"

def _append_filename_to_name_param(path: str, filename: str) -> str:
    if filename and path.endswith("name="): return f"{path}{filename}"
    return path

def _mgmt_default_path_for(action: str) -> str:
    a = (action or "").upper()
    return "/query" if a.startswith("GET") else MGMT_DEFAULT_PATH

# ---------------- Assertions ----------------

def assert_status(r: requests.Response, expected: int) -> None:
    assert r.status_code == expected, f"status={r.status_code} body={r.text[:200]}"

def assert_ct_contains(r: requests.Response, needle: str) -> None:
    ct = (r.headers.get("Content-Type") or "").lower()
    n = (needle or "").lower()
    if n == "xml": ok = ("xml" in ct)
    elif n == "json": ok = ("json" in ct)
    elif n in ("text","txt"): ok = ("text/" in ct) or ("xml" in ct) or ("json" in ct)
    else: ok = (n in ct)
    assert ok, f"Content-Type '{ct}' does not contain '{needle}'"

def assert_headers_contains(r: requests.Response, pairs: Dict[str, str]) -> None:
    low = {k.lower(): v for k, v in r.headers.items()}
    missing = {k: v for k, v in pairs.items() if low.get(k.lower(), "").lower() != v.lower()}
    assert not missing, f"Missing/unequal headers: {missing}, got: {r.headers}"

def assert_text_regex(r: requests.Response, pattern: str) -> None:
    assert re.search(pattern, r.text, re.MULTILINE), f"Regex not matched: {pattern}"

# ---------------- XML helpers ----------------

DYNAMIC_TAGS = {"Source","Sender","ModuleURI","Module","Created"}

def _strip_dynamic_xml(root: "etree._Element") -> None:
    if etree is None: return
    ns_uri = root.nsmap.get(None, "http://www.fdsn.org/xml/station/1")
    for tag in DYNAMIC_TAGS:
        for el in root.findall(f".//{{{ns_uri}}}{tag}"):
            parent = el.getparent()
            if parent is not None: parent.remove(el)

def _xml_c14n_bytes(el: "etree._Element") -> bytes:
    try: return etree.tostring(el, method="c14n2")
    except Exception: return etree.tostring(el, method="c14n")

def _dump_last_xml(kind: str, content: bytes) -> None:
    out = EXPECTED_DIR / f"_last_{kind}.xml"
    try: out.write_bytes(content)
    except Exception: pass

def assert_xml_equals_file(cfg, r: requests.Response, filename: str) -> None:
    if etree is None: pytest.skip("lxml not installed; XML checks skipped")
    p = EXPECTED_DIR / filename
    if cfg.update_snapshots:
        p.write_text(r.text, encoding="utf-8"); return
    assert p.is_file(), f"Golden not found: {p}"
    try:
        resp_root = etree.fromstring(r.content)
        exp_bytes = p.read_bytes()
        exp_root  = etree.fromstring(exp_bytes)
    except Exception as exc:
        raise AssertionError(f"Invalid XML parse: {exc}") from exc

    _strip_dynamic_xml(resp_root); _strip_dynamic_xml(exp_root)
    r_bytes = _xml_c14n_bytes(resp_root)
    e_bytes = _xml_c14n_bytes(exp_root)

    # OUTPUT XML: independent fraction/Z
    z_mode, f_mode = _output_modes_for(cfg, "xml")
    e_txt = e_bytes.decode("utf-8", errors="replace")
    e_txt = _apply_modes(e_txt, z_mode, f_mode)
    e_bytes = e_txt.encode("utf-8")

    if r_bytes != e_bytes:
        _dump_last_xml("expected", e_bytes); _dump_last_xml("actual", r_bytes)
        try:
            r_pretty = etree.tostring(etree.fromstring(r_bytes), pretty_print=True)
            e_pretty = etree.tostring(etree.fromstring(e_bytes), pretty_print=True)
        except Exception:
            r_pretty, e_pretty = r_bytes, e_bytes
        diff = diff_texts(e_pretty, r_pretty, fromfile=str(p), tofile="<response>", n=60)
        raise AssertionError(
            f"XML canonical forms differ "
            f"(Z={z_mode}, fraction={f_mode}).\n\n{diff}"
        )

# ---------------- Case model ----------------

@dataclass
class Case:
    name: str
    method: str
    path: str
    headers: Dict[str, str] | Callable[[], Dict[str, str]] = None
    body_file: Optional[str] = None
    body_text: Optional[str] = None
    expect: Dict[str, Any] = None
    group: Optional[str] = None
    action: Optional[str] = None
    file_name: Optional[str] = None
    auth: Optional[Tuple[str, str]] = None
    comment: Optional[str] = None
    def __post_init__(self) -> None:
        self.headers = self.headers or {}
        self.expect  = self.expect or {}
    def eval_headers(self) -> Dict[str, str]:
        return self.headers() if callable(self.headers) else self.headers

# ---------------- Smoke helper ----------------

def _pick_any_stationxml(data_dir: Path) -> Optional[str]:
    paths = sorted(glob.glob(str(data_dir) + "/**/*.xml", recursive=True))
    return paths[0] if paths else None

# ---------------- Mapping loader (YAML/JSON/CSV) ----------------

def _looks_like_inline_content(s: str) -> bool:
    if not s: return False
    t = s.strip()
    return ("\n" in t) or t.startswith(("<?xml","<","{","[")) or (">" in t)

def _auto_materialize_golden(group: str, idx: int, _comment: str, raw: str) -> str:
    ftype = "xml" if raw.strip().startswith("<") else ("json" if raw.strip().startswith(("{","[")) else "txt")
    fname = f"{group}_{idx:03d}.{ftype}.golden"
    (EXPECTED_DIR / fname).write_text(raw, encoding="utf-8")
    return fname

def _golden_is_html(fname: str) -> bool:
    try:
        head = (EXPECTED_DIR / fname).read_text(encoding="utf-8")[:200].lstrip().lower()
        return head.startswith("<!doctype html") or head.startswith("<html")
    except Exception:
        return False

def _golden_is_xml_fragment(fname: str) -> bool:
    if etree is None: return False
    p = EXPECTED_DIR / fname
    if not p.is_file(): return False
    try:
        etree.fromstring(p.read_bytes())
        return False
    except Exception:
        return True

def _mapping_path() -> Path:
    for name in ("_mapping.yaml", "_mapping.yml", "_mapping.json", "_mapping.csv"):
        p = EXPECTED_DIR / name
        if p.is_file(): return p
    return EXPECTED_DIR / "_mapping.csv"

def _iter_records_from_mapping(mp: Path) -> List[Dict[str, Any]]:
    if mp.suffix.lower() in (".yaml", ".yml"):
        if yaml is None:
            raise RuntimeError("PyYAML not installed but _mapping.yaml found. Install pyyaml or convert mapping.")
        data = yaml.safe_load(mp.read_text(encoding="utf-8")) or []
        if isinstance(data, dict) and "records" in data:
            data = data["records"]
        if not isinstance(data, list):
            raise RuntimeError("YAML mapping must be a list of records or {records: [...]} object.")
        return list(data)
    if mp.suffix.lower() == ".json":
        data = json.loads(mp.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "records" in data:
            data = data["records"]
        if not isinstance(data, list):
            raise RuntimeError("JSON mapping must be an array of records or {records:[...]}.")
        return list(data)
    return list(csv.DictReader(mp.open("r", encoding="utf-8", newline="")))

def _csv_int(s: str, default: int = 200) -> int:
    try: return int((s or "").strip())
    except Exception: return default

def _load_cases_from_mapping() -> tuple[list[Case], list[Case]]:
    mp = _mapping_path()
    rows = _iter_records_from_mapping(mp)
    legacy: List[Case] = []; mgmt: List[Case] = []
    for row in rows:
        group    = (row.get("group") or "").strip()
        idx_s    = (row.get("index") or "0").strip() if isinstance(row.get("index"), str) else row.get("index", 0)
        try: idx = int(idx_s)
        except Exception: idx = 0

        name     = (row.get("name") or "legacy_case").strip()
        method   = (row.get("method") or "GET").strip().upper()
        path     = (row.get("path") or "/query").strip()
        query    = (row.get("query") or "").strip()
        status   = _csv_int(row.get("expected_status"), 200)
        golden   = (row.get("filename") or "").strip()
        ctype    = (row.get("ctype") or "").strip().lower()
        comment  = (row.get("comment") or "").strip()
        match    = (row.get("match") or "").strip().lower()
        action   = (row.get("action") or "").strip().upper()
        file_name= (row.get("file_name") or "").strip()
        file_dir = (row.get("file_dir") or "").strip()
        version  = (row.get("version") or "").strip()

        if group == "test_management":
            if action in ("PUT","PUT_LOCK_CACHE"): method = "PUT"
            elif action.startswith("GET"): method = "GET"
            elif action.startswith("POST"): method = "POST"
            else: method = "DELETE"

        if group == "test_management" and _looks_like_inline_content(path):
            golden = _auto_materialize_golden(group or "case", idx, comment, path)
            if golden.endswith(".xml.golden") and not ctype: ctype = "xml"
            if golden.endswith(".txt.golden"):
                if not ctype: ctype = "text"
                if not match: match = "startswith"
            path = _mgmt_default_path_for(action)

        if group == "test_management":
            desired_default = _mgmt_default_path_for(action)
            if path == MGMT_DEFAULT_PATH and desired_default != MGMT_DEFAULT_PATH:
                path = desired_default

        if action == "GETXML" and not ctype: ctype = "xml"
        if action == "GETTEXT" and not ctype: ctype = "text"

        exp: Dict[str, Any] = {"status": status}
        if golden: exp["body_equals_file"] = golden

        if golden and (_golden_is_html(golden) or ((ctype == "xml") and _golden_is_xml_fragment(golden))):
            ctype = "text"
            if not match: match = "startswith"

        if ctype: exp["content_type_contains"] = ctype
        if match: exp["match"] = match

        headers: Dict[str, str] = {}
        body_text = None
        body_file = None
        auth = None

        if version:
            headers["User-Agent"] = f"ObsPy/{version}"

        if action in ("PUT","PUT_LOCK_CACHE","POST"):
            if file_dir and file_name:
                body_file = str(Path(file_dir) / file_name)
            headers.setdefault("Content-Type","application/octet-stream")
            if group == "testdataio" and file_name:
                headers["filename"] = file_name
            if action == "PUT_LOCK_CACHE":
                headers["lockseconds"] = "0"
        elif action == "DELETE":
            if file_name:
                headers["filename"] = file_name
        elif action in ("GET","GETTEXT","GETXML"):
            path = _append_filename_to_name_param(path, file_name)

        if method in ("GET","DELETE") or (group == "test_management"):
            path = _attach_query(path, query)
        if method == "POST":
            body_text = query
            headers.setdefault("Content-Type", "application/x-www-form-urlencoded" if version else "application/octet-stream")

        c = Case(
            name=name, method=method, path=path,
            headers=headers, body_file=body_file, body_text=body_text,
            expect=exp, group=group or None, action=action or None,
            file_name=file_name or None, auth=auth, comment=comment or None,
        )
        (mgmt if group == "test_management" else legacy).append(c)

    return legacy, mgmt

# storage filled by pytest_generate_tests
_LOADED_LEGACY: List[Case] = []
_LOADED_MGMT: List[Case] = []

# ---------------- Request/Assert runners ----------------

def _apply_input_normalization(cfg, payload: str) -> str:
    # INPUT side: independent fraction + Z
    payload = normalize_fractional_seconds(payload, getattr(cfg, "in_fraction_mode", "as-is"))
    payload = normalize_trailing_z(payload, getattr(cfg, "in_z_mode", "as-is"))
    return payload

def _do_request(http: requests.Session, cfg, case: Case) -> requests.Response:
    url = build_url(cfg, case.path)
    headers = {k: v for k, v in (case.eval_headers() or {}).items() if v is not None}
    data: Optional[bytes | str] = None

    if case.body_file:
        raw = read_bytes(case.body_file).decode("utf-8", errors="replace")
        raw = _apply_input_normalization(cfg, raw)
        data = raw.encode("utf-8")
        headers.setdefault("Content-Type","application/octet-stream")
        if case.action in ("PUT","PUT_LOCK_CACHE") and "filename" not in headers and case.file_name:
            headers["filename"] = case.file_name
        if case.action == "DELETE" and "filename" not in headers and case.file_name:
            headers["filename"] = case.file_name
        if case.action == "PUT_LOCK_CACHE":
            headers.setdefault("lockseconds","1")
    elif case.body_text is not None:
        raw = str(case.body_text)
        raw = _apply_input_normalization(cfg, raw)
        data = raw
        headers.setdefault("Content-Type","application/octet-stream")

    auth = requests.auth.HTTPBasicAuth(*case.auth) if case.auth else requests.auth.HTTPBasicAuth(*cfg.default_auth)

    if case.action == "DELETE_MULTI":
        return http.delete(url, headers=headers, timeout=cfg.timeout_s, auth=auth)
    return http.request(case.method, url, headers=headers, data=data, timeout=cfg.timeout_s, auth=auth)

def _is_json_expected(ctt: str, filename: str) -> bool:
    ctt = (ctt or "").lower()
    if "json" in ctt:
        return True
    return filename.lower().endswith(".json.golden")

def _json_equal_text(body: str, expected: str) -> bool:
    try:
        a = json.loads(body)
        b = json.loads(expected)
    except Exception:
        return False
    return a == b

def _json_unified_diff(body: str, expected: str) -> str:
    try:
        a_obj = json.loads(body)
        b_obj = json.loads(expected)
    except Exception as e:
        return f"<< invalid JSON for diff: {e} >>"
    a_pretty = json.dumps(a_obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    b_pretty = json.dumps(b_obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    return "".join(
        difflib.unified_diff(b_pretty.splitlines(True), a_pretty.splitlines(True),
                             fromfile="expected", tofile="actual", lineterm="")
    )

def _assert_match_mode(cfg, r: "requests.Response", exp: dict) -> None:
    if "body_equals_file" not in exp:
        return

    filename = str(exp["body_equals_file"])
    mode = (exp.get("match") or "").lower()
    ctt = (exp.get("content_type_contains") or "").lower()

    # XML branch
    if ctt == "xml":
        assert_xml_equals_file(cfg, r, filename)
        return

    # TEXT/JSON branch
    p = EXPECTED_DIR / filename
    if getattr(cfg, "update_snapshots", False) and mode != "startswith":
        p.write_text(r.text, encoding="utf-8")
        return

    expected = p.read_text(encoding="utf-8") if p.is_file() else ""
    is_json = _is_json_expected(ctt, filename)

    if is_json:
        z_mode, f_mode = _output_modes_for(cfg, "json")
        expected = _apply_modes(expected, z_mode, f_mode)
    else:
        z_mode, f_mode = _output_modes_for(cfg, "text")
        expected = _apply_modes(expected, z_mode, f_mode)

    if mode == "startswith":
        assert r.text.startswith(expected), f"Body does not start with expected from {filename}"
        return

    if is_json:
        ok = _json_equal_text(r.text, expected)
        if not ok and getattr(cfg, "json_diff", False):
            diff = _json_unified_diff(r.text, expected)
            raise AssertionError(f"JSON body mismatch vs {filename}\n\n{diff}")
        assert ok, f"JSON body mismatch vs {filename}"
        return

    assert r.text == expected, f"Body mismatch vs {filename}"

def _sanitize_expect_for_method(case: Case, exp: Dict[str, Any]) -> Dict[str, Any]:
    if case.method in ("PUT","DELETE"):
        exp = dict(exp)
        for k in ("content_type_contains","body_equals_file","xml_xpath_exists","xml_xpath_count","xml_text_contains","text_regex"):
            exp.pop(k, None)
    return exp

def _run_case(http: requests.Session, cfg, case: Case) -> None:
    if "skip" in (case.expect or {}): pytest.skip(str(case.expect["skip"]))
    r = _do_request(http, cfg, case)
    exp = _sanitize_expect_for_method(case, case.expect or {})
    if "status" in exp: assert_status(r, int(exp["status"]))
    if "content_type_contains" in exp: assert_ct_contains(r, str(exp["content_type_contains"]))
    if "headers_contains" in exp: assert_headers_contains(r, dict(exp["headers_contains"]))
    if "body_equals_file" in exp: _assert_match_mode(cfg, r, exp)
    if "text_regex" in exp: assert_text_regex(r, str(exp["text_regex"]))

def _case_id(case: Case) -> str:
    c = (case.comment or "").strip()
    if c:
        short = (c[:80] + "…") if len(c) > 80 else c
        return f"{case.name} - {short}"
    return case.name

# ---------------- Collection-time param injection ----------------

def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "case" not in metafunc.fixturenames:
        return
    global _LOADED_LEGACY, _LOADED_MGMT
    if not _LOADED_LEGACY and not _LOADED_MGMT:
        _LOADED_LEGACY, _LOADED_MGMT = _load_cases_from_mapping()

    func_name = metafunc.function.__name__
    if func_name == "test_integration_legacy":
        params = _LOADED_LEGACY
    elif func_name == "test_management_cases":
        params = _LOADED_MGMT
    else:
        params = []
    metafunc.parametrize("case", params, ids=[_case_id(c) for c in params])

# ---------------- Tests ----------------

@pytest.mark.smoke
def test_smoke(http: requests.Session, cfg) -> None:
    r = http.get(build_url(cfg, "/version"), timeout=cfg.timeout_s)
    assert_status(r, 200); assert_ct_contains(r, "text"); assert_text_regex(r, r"^\d+\.\d+(\.\d+)?$")
    any_xml = _pick_any_stationxml(cfg.data_dir)
    if any_xml and cfg.provider:
        filename = f"{cfg.provider}_{Path(any_xml).stem}.xml"
        r = http.put(build_url(cfg, "/query"), data=read_bytes(any_xml),
                     headers={"filename": filename, "Content-Type":"application/octet-stream"},
                     timeout=cfg.timeout_s)
        assert_status(r, 200)
        r = http.delete(build_url(cfg, "/query"), headers={"filename": filename}, timeout=cfg.timeout_s)
        assert_status(r, 200)

@pytest.mark.integration
def test_integration_legacy(http: requests.Session, cfg, case: Case) -> None:
    _run_case(http, cfg, case)

@pytest.mark.management
def test_management_cases(http: requests.Session, cfg, case: Case) -> None:
    _run_case(http, cfg, case)
