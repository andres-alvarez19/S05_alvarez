"""Ejecuta los seis archivos JSONL de contrato en directorios aislados."""
from __future__ import annotations
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from s05.engine import ToolRunner


def stage(target: Path) -> None:
    for name in ["tools/tools.manifest.json", "INPUT/raw/defect_reports.json",
                 "INPUT/raw/defect_report_sample.md"]:
        output = target / name
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, output)
    shutil.copytree(ROOT / "schemas", target / "schemas")


def execute_suite() -> int:
    files = sorted((ROOT / "evals/tools").rglob("*.jsonl"))
    if len(files) != 6:
        print(f"FAIL: se esperaban 6 archivos JSONL, encontrados {len(files)}")
        return 1
    failures = []
    for case_path in files:
        for row in case_path.read_text(encoding="utf-8").splitlines():
            if not row.strip():
                continue
            case = json.loads(row)
            with tempfile.TemporaryDirectory(prefix="s05-case-") as tmp:
                temp_root = Path(tmp)
                stage(temp_root)
                result = ToolRunner(temp_root).invoke(case["tool_id"], case["input"], role=case["role"])
                differences = [(key, expected, result.get(key))
                               for key, expected in case["expect"].items()
                               if key != "items_count" and result.get(key) != expected]
                if "items_count" in case["expect"]:
                    if len(result.get("items", [])) != case["expect"]["items_count"]:
                        differences.append(("items_count", case["expect"]["items_count"], len(result.get("items", []))))
                if result["ok"] and "artifact_path" in result and not (temp_root / result["artifact_path"]).is_file():
                    differences.append(("artifact_path", "existe", "no existe"))
                if differences:
                    failures.append((case["case_id"], differences))
                    print(f"FAIL {case['case_id']}: {differences}")
                else:
                    print(f"PASS {case['case_id']}: contrato y expectativa verificados")
    print(f"RESULTADO: {6 - len(failures)}/6 casos válidos")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(execute_suite())
