# R4 · Errores accionables

Se reescriben tres errores del mazo y un error de la herramienta propia. Los errores E-1 y E-2 originales no contienen detalles suficientes para inferir el campo: sus causas se declaran **supuestos explícitos del ejercicio**, no hechos constatados.

## E-1 «Error 400» — ejemplo supuesto
- **Categoría:** ERROR_ARGUMENTOS.
- **Causa concreta:** campo `case_id` recibido `<ausente>`, esperado `TC-[A-Z0-9-]{1,16}`.
- **Camino de salida:** añadir `case_id: "TC-S05-A1"` a la petición; validar contra su schema.
- **Política:** reintentar **una sola vez** con el campo agregado; nunca repetir el mismo JSON.

## E-2 «invalid input» — ejemplo supuesto
- **Categoría:** ERROR_ARGUMENTOS.
- **Causa concreta:** `page_size=-1`, esperado entero de 1 a 3.
- **Camino de salida:** ejecutar `consultar_informes_defecto` con `page_size:2`.
- **Política:** reintentar **una sola vez con cambio**; si persiste, detenerse.

## E-3 «BAD_RUT; rut inválido»
- **Categoría:** ERROR_ARGUMENTOS.
- **Causa concreta de ejemplo:** `rut="12.345.678-9"` con puntos; esperado patrón `^[0-9]{7,8}-[0-9Kk]$`, además de dígito verificador correcto.
- **Camino de salida:** eliminar puntos, normalizar K a mayúscula y comprobar el dígito verificador antes de llamar; si no verifica, solicitar dato correcto.
- **Política:** una llamada corregida si pasó validación; si no, no reintentar. El RUT es ejemplo del mazo, no parte de T1.

## Error real de nuestra herramienta registrar_prueba_defecto
- **Entrada:** report_id=DEF-001, case_id=TC-S05-A2, idempotency_key=DEF-002:TC-S05-A2.
- **Categoría:** ERROR_ARGUMENTOS.
- **Causa:** clave recibida DEF-002:TC-S05-A2, esperada DEF-001:TC-S05-A2.
- **Camino de salida:** reemplazar únicamente la clave por DEF-001:TC-S05-A2.
- **Política:** una vez con argumentos corregidos; nunca repetir tupla idéntica.
- **Evidencia ejecutable:** evals/tools/registrar_prueba/error_recuperable.jsonl.

## Detección de tupla repetida en el arnés

El método `ToolRunner.invoke` calcula la representación JSON canónica de `(tool_id, arguments)`. Si una llamada falla, agrega su firma a `failed_calls`; si se repite una llamada fallida idéntica, corta **antes de ejecutar** y devuelve `repeated_failed_call` con categoría ERROR_BUCLE, recoverable=false y retry_policy=never. Una petición corregida puede pasar nuevamente por esquema, roles y límites. Prueba: `test_identical_failed_call_is_blocked`.
