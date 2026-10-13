"""Dos herramientas T1: lectura paginada y escritura idempotente confinada a WORK."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


READ = "consultar_informes_defecto"
WRITE = "registrar_prueba_defecto"
SCHEMAS = {
    READ: ("consultar_informes.in.json", "consultar_informes.out.json"),
    WRITE: ("registrar_prueba.in.json", "registrar_prueba.out.json"),
}


def make_error(code: str, category: str, field: str, received: Any,
               expected: str, action: str, *, recoverable: bool = False) -> dict:
    return {
        "ok": False, "error_code": code, "category": category,
        "cause": {"field": field, "received": str(received)[:120],
                  "expected": expected},
        "next_action": action,
        "retry_policy": "retry_once_with_change" if recoverable else "never",
        "recoverable": recoverable,
    }


class ToolRunner:
    """Puerta única con allowlist por rol, JSON Schema y corte de bucle de error."""

    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.manifest = json.loads((self.root / "tools/tools.manifest.json").read_text(encoding="utf-8"))
        self.failed_calls: set[str] = set()

    def _schema(self, name: str) -> dict:
        return json.loads((self.root / "schemas/tools" / name).read_text(encoding="utf-8"))

    def invoke(self, tool_id: str, arguments: dict, *, role: str) -> dict:
        # No se acepta una herramienta ausente del manifiesto; se comprueba antes del dispatch.
        if tool_id not in SCHEMAS or tool_id not in self.manifest.get("roles", {}).get(role, []):
            return make_error("policy_denied", "ERROR_PERMISO", "tool_id",
                              tool_id, "herramienta registrada y rol autorizado",
                              "Solicite el permiso mínimo correspondiente; no vuelva a invocar.")
        if not isinstance(arguments, dict):
            return make_error("schema_invalid", "ERROR_ARGUMENTOS", "arguments", type(arguments).__name__,
                              "objeto JSON", "Envíe un objeto JSON válido.", recoverable=True)
        signature = json.dumps([tool_id, arguments], sort_keys=True, ensure_ascii=False)
        if signature in self.failed_calls:
            return make_error("repeated_failed_call", "ERROR_BUCLE", "(herramienta, argumentos)",
                              "repetidos", "argumentos modificados tras error recuperable",
                              "Detenga la llamada idéntica; cambie el campo indicado o aborte.")
        in_name, out_name = SCHEMAS[tool_id]
        problem = next(iter(Draft202012Validator(self._schema(in_name)).iter_errors(arguments)), None)
        if problem:
            field = ".".join(map(str, problem.absolute_path)) or "(objeto raíz)"
            result = make_error("schema_invalid", "ERROR_ARGUMENTOS", field,
                                "entrada no válida", str(problem.message)[:160],
                                "Corrija el campo según el esquema y reintente una sola vez.",
                                recoverable=True)
        else:
            try:
                result = self._read(arguments) if tool_id == READ else self._write(arguments)
            except (OSError, ValueError, KeyError, TypeError):
                result = make_error("tool_failed", "ERROR_ESTADO", "operación", "fallo interno",
                                    "recurso y esquema disponibles",
                                    "Detenga la invocación; revise la traza segura y el entorno.")
        if result["ok"]:
            valid = Draft202012Validator(self._schema(out_name))
        else:
            valid = Draft202012Validator(self._schema("error.json"))
        if not valid.is_valid(result):
            result = make_error("output_schema_invalid", "ERROR_ESTADO", "result", "inválido",
                                "esquema de salida declarado",
                                "Detenga la ejecución y corrija el contrato antes de continuar.")
        if not result["ok"]:
            self.failed_calls.add(signature)
        return result

    def _read(self, args: dict) -> dict:
        source = self.root / "INPUT/raw/defect_reports.json"
        records = json.loads(source.read_text(encoding="utf-8"))["records"]
        ids = set(args.get("report_ids", []))
        if ids:
            records = [item for item in records if item["report_id"] in ids]
        # La opción status está documentada para el corpus de laboratorio, totalmente disponible.
        records = sorted(records, key=lambda item: item["report_id"])
        total = len(records)
        cursor = args.get("cursor", 0)
        size = args.get("page_size", 2)
        items = records[cursor:cursor + size]
        next_cursor = cursor + len(items) if cursor + len(items) < total else None
        return {
            "ok": True, "items": items, "total_disponible": total,
            "devueltos": len(items), "cursor_siguiente": next_cursor,
            "truncado": next_cursor is not None,
            "como_refinar": "Use report_ids o cursor_siguiente para continuar; page_size máximo 3.",
        }

    def _write(self, args: dict) -> dict:
        report_id, case_id = args["report_id"], args["case_id"]
        key = args["idempotency_key"]
        expected_key = f"{report_id}:{case_id}"
        if key != expected_key:
            return make_error("invalid_idempotency_key", "ERROR_ARGUMENTOS", "idempotency_key",
                              key, expected_key, f"Use exactamente {expected_key}.", recoverable=True)
        if report_id != "DEF-001":
            return make_error("insufficient_evidence", "ERROR_ARGUMENTOS", "report_id",
                              report_id, "DEF-001 (informe fuente documentado)",
                              "Consulte la evidencia y obtenga una aserción verificable antes de crear pruebas.")
        source = (self.root / "INPUT/raw/defect_report_sample.md").read_text(encoding="utf-8")
        if "ID: DEF-001" not in source or "comment" not in source:
            return make_error("source_mismatch", "ERROR_ESTADO", "source", "no coincide",
                              "ID DEF-001 y evidencia campo opcional comment",
                              "Detenga la escritura; revise la fuente sellada.")
        template = (
            "# Generado para DEF-001; clave de idempotencia: " + key + "\n"
            "from target_demo.converter import convert\n"
            "\n"
            "def test_" + case_id.replace("-", "_").lower() + "():\n"
            "    observed = convert({'value': 'ejemplo'})\n"
            "    assert observed['ok'] is True, 'DEF-001: comment debe ser opcional'\n"
        )
        workspace = self.root / "WORK/tests"
        workspace.mkdir(parents=True, exist_ok=True)
        # El destino nunca puede escapar de WORK mediante enlaces simbólicos.
        if not workspace.resolve().is_relative_to(self.root / "WORK"):
            return make_error("path_violation", "ERROR_PERMISO", "workspace", "ruta fuera de WORK",
                              "WORK/tests", "Deniegue la escritura y revise el montaje del sandbox.")
        artifact = workspace / f"{case_id}.py"
        if artifact.exists():
            if artifact.read_text(encoding="utf-8") != template:
                return make_error("write_once_conflict", "ERROR_ESTADO", "case_id", case_id,
                                  "artefacto inmutable con idéntico contenido",
                                  "Use un case_id nuevo; no sobrescriba una prueba publicada.")
            effect = "replayed"
        else:
            try:
                with artifact.open("x", encoding="utf-8") as handle:
                    handle.write(template)
            except FileExistsError:
                return make_error("write_once_conflict", "ERROR_ESTADO", "case_id", case_id,
                                  "ruta desocupada", "Use un case_id nuevo; no sobrescriba.")
            effect = "created"
        lines = template.splitlines()
        preview_count = args.get("preview_lines", 6)
        truncated = len(lines) > preview_count
        return {
            "ok": True, "artifact_path": f"WORK/tests/{case_id}.py",
            "idempotency_key": key, "effect": effect,
            "preview": lines[:preview_count],
            "total_disponible": len(lines), "devueltos": min(preview_count, len(lines)),
            "cursor_siguiente": preview_count if truncated else None,
            "truncado": truncated,
            "como_refinar": "Vuelva a consultar con preview_lines mayor, misma clave, o lea el archivo local WORK/tests.",
        }
