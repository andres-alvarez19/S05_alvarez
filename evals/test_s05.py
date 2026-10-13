"""Pruebas de contrato, permisos, idempotencia y reproducción real del defecto."""
from __future__ import annotations
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from s05.engine import READ, WRITE, ToolRunner
from s05.capabilities import audit_simulated_capabilities

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def factory(tmp_path: Path) -> ToolRunner:
    shutil.copytree(ROOT / "schemas", tmp_path / "schemas")
    (tmp_path / "tools").mkdir()
    shutil.copy(ROOT / "tools/tools.manifest.json", tmp_path / "tools/tools.manifest.json")
    (tmp_path / "INPUT/raw").mkdir(parents=True)
    for name in ["defect_reports.json", "defect_report_sample.md"]:
        shutil.copy(ROOT / "INPUT/raw" / name, tmp_path / "INPUT/raw" / name)
    return ToolRunner(tmp_path)


def request(case="TC-S05-TEST", preview=10):
    return {"report_id": "DEF-001", "case_id": case,
            "idempotency_key": f"DEF-001:{case}", "assertion": "accepts_without_optional_comment",
            "preview_lines": preview}


def test_six_jsonl_cases_execute():
    from scripts.run_tool_evals import execute_suite
    assert execute_suite() == 0


def test_read_paginates_with_total_and_cursor(factory):
    first = factory.invoke(READ, {"page_size": 1}, role="analyst")
    second = factory.invoke(READ, {"page_size": 1, "cursor": first["cursor_siguiente"]}, role="analyst")
    assert first["ok"] and first["truncado"] and first["total_disponible"] == 3
    assert first["items"][0]["report_id"] != second["items"][0]["report_id"]


def test_write_replay_is_idempotent(factory):
    first = factory.invoke(WRITE, request(), role="writer")
    path = factory.root / first["artifact_path"]
    original = path.read_bytes()
    second = factory.invoke(WRITE, request(), role="writer")
    assert first["effect"] == "created" and second["effect"] == "replayed"
    assert path.read_bytes() == original


def test_write_once_conflict_does_not_overwrite(factory):
    first = factory.invoke(WRITE, request(), role="writer")
    path = factory.root / first["artifact_path"]
    path.write_text("otro contenido", encoding="utf-8")
    result = factory.invoke(WRITE, request(), role="writer")
    assert not result["ok"] and result["error_code"] == "write_once_conflict"
    assert path.read_text(encoding="utf-8") == "otro contenido"


def test_role_separation_and_default_deny(factory):
    assert factory.invoke(WRITE, request(), role="analyst")["error_code"] == "policy_denied"
    assert factory.invoke(READ, {}, role="writer")["error_code"] == "policy_denied"
    assert factory.invoke("shell", {}, role="writer")["error_code"] == "policy_denied"


def test_identical_failed_call_is_blocked(factory):
    bad = {"page_size": 0}
    assert factory.invoke(READ, bad, role="analyst")["error_code"] == "schema_invalid"
    repeat = factory.invoke(READ, bad, role="analyst")
    assert repeat["error_code"] == "repeated_failed_call"
    assert repeat["retry_policy"] == "never"
    assert factory.invoke(READ, {"page_size": 1}, role="analyst")["ok"]


def test_additional_properties_denied(factory):
    result = factory.invoke(READ, {"invented_field": "silencioso"}, role="analyst")
    assert result["error_code"] == "schema_invalid"


def test_bad_idempotency_key_has_actionable_error(factory):
    value = request()
    value["idempotency_key"] = "DEF-002:TC-S05-TEST"
    error = factory.invoke(WRITE, value, role="writer")
    assert error["category"] == "ERROR_ARGUMENTOS"
    assert error["cause"]["field"] == "idempotency_key"
    assert error["retry_policy"] == "retry_once_with_change"
    assert error["next_action"]


def test_preview_truncation_is_explicit(factory):
    result = factory.invoke(WRITE, request(preview=1), role="writer")
    assert result["truncado"] and result["total_disponible"] > result["devueltos"]
    assert result["cursor_siguiente"] == 1 and result["como_refinar"]


def test_generated_pytest_reproduces_observed_defect(factory):
    result = factory.invoke(WRITE, request(), role="writer")
    assert result["ok"]
    path = factory.root / result["artifact_path"]
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    run = subprocess.run([sys.executable, "-m", "pytest", "-q", str(path)],
                         cwd=ROOT, env=env, capture_output=True, text=True)
    # Se exige fallo por aserción sobre valor observado: no fallos de sintaxis ni import.
    assert run.returncode == 1
    assert "AssertionError: DEF-001: comment debe ser opcional" in run.stdout
    assert "1 failed" in run.stdout


def test_schema_contracts_strict():
    files = list((ROOT / "schemas/tools").glob("*.json"))
    assert len(files) == 5
    for file in files:
        schema = json.loads(file.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False


def test_simulated_external_audit_no_actual_permissions():
    results = audit_simulated_capabilities(ROOT)
    assert len(results) == 5
    eligible = {r["capability_id"] for r in results if r["simulated_candidate"]}
    assert eligible == {"fetch_issue"}
    assert all(not r["operational_access"] for r in results)
    for cap in ("search_code", "publish_report", "export_secrets", "run_shell"):
        assert next(r for r in results if r["capability_id"] == cap)["pre_gate"] == "quarantine_or_deny"
