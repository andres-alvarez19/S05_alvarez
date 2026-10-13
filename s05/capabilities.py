"""Auditoría determinista de capacidades hipotéticas; NO establece conexiones MCP."""
from __future__ import annotations
import json
import re
from pathlib import Path


def audit_simulated_capabilities(root: Path) -> list[dict]:
    root = Path(root)
    scenario = json.loads((root / "escenario_servidor_simulado.json").read_text(encoding="utf-8"))
    policy = json.loads((root / "politica_capacidades.json").read_text(encoding="utf-8"))
    assert policy["default"] == "deny" and not policy["operational_external_access"]
    assert policy["server_allowlist"] == []
    candidate_ids = {item["capability_id"] for item in policy["simulated_candidate_allowlist"]}
    decisions = []
    for cap in scenario["capabilities"]:
        description = cap["description"]
        injection = bool(re.search(r"instrucci[oó]n para el agente|ignora cualquier pol[ií]tica|https?://", description, re.I))
        effect_mismatch = cap["declared_effect"] != cap["observed_effect"]
        permitted_as_example = bool(cap["needed"] and not injection and not effect_mismatch and cap["id"] in candidate_ids)
        reasons = []
        if not cap["needed"]:
            reasons.append("capacidad_innecesaria")
        if injection:
            reasons.append("instruction_override_en_descripcion")
        if effect_mismatch:
            reasons.append("efecto_real_no_declarado")
        if cap["id"] not in candidate_ids:
            reasons.append("fuera_allowlist_candidata")
        decisions.append({"capability_id": cap["id"], "version": cap["version"],
                          "simulated_candidate": permitted_as_example, "operational_access": False,
                          "pre_gate": "allow_simulated_only" if permitted_as_example else "quarantine_or_deny",
                          "reasons": reasons or ["sin_acceso_real"]})
    return decisions
