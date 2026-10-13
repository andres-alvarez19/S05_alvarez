"""Ruta de ejemplo CON DEFECTO conocido: exige indebidamente comment opcional."""


def convert(payload: dict) -> dict:
    if "comment" not in payload:
        return {"ok": False, "error": "missing comment"}
    return {"ok": True, "value": payload.get("value")}
