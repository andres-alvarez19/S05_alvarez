# Bitácora — Semana 5 · Auditoría del pañol

Fábrica T1: transformar informes de defectos admitidos en casos pytest ejecutables o abstenerse si falta evidencia. Referencias: repositorios S03_Alvarez y S04_Alvarez.

## R1 · Auditoría del catálogo sembrado (15 min)

La lista de doce puntos se aplica al catálogo de siete herramientas de la guía. Se identifican siete hallazgos individuales con consecuencia concreta; también el solapamiento H-2/H-3 y H-5/H-6 (punto 12). El punto 11 requiere idempotencia y separación de escrituras, que el catálogo **no documenta** y por ello se marca «no verificable», sin fingir conocer su código. Rediseño de siete a tres: obtener_caso, listar_casos y cambiar_estado_caso. Matriz y justificaciones: `auditoria.md`.

## R2 · Dos fichas y seis casos

La fábrica utiliza dos herramientas **sin disparadores solapados**:

- `consultar_informes_defecto`: read_only, role:analyst, filtros por ID, página por defecto 2, máximo 3, total disponible, devueltos, cursor, truncado y sugerencia para refinar.
- `registrar_prueba_defecto`: write_sandbox, role:writer, solo WORK/tests, genera una prueba de regresión para DEF-001. Clave `report_id:case_id`, replay idempotente sin sobreescritura. Vista previa por defecto 6 líneas y máximo 40, con metadatos al truncarse.

Las fichas están en tools/*.tool.yaml, esquemas JSON en schemas/tools y permisos en tools/tools.manifest.json. Cada herramienta tiene **éxito, error recuperable y límite** como archivo JSONL ejecutable bajo evals/tools/. DEF-001 procede del informe original conservado de S03; DEF-002 y DEF-003 son registros sintéticos identificados como tales, para probar paginación.

## R3 · Auditoría cruzada

**NO REALIZADA POR IMPOSIBILIDAD DE CONSEGUIR REVISIÓN CRUZADA.** No se obtuvo catálogo de un compañero ni retroalimentación sobre el propio. Los tres escenarios y el hallazgo de puntos 11/12 de un catálogo ajeno no pudieron ejecutarse. Se registra la limitación sin inventar contraparte, conclusiones ni evidencias. Este criterio de la actividad queda sin cumplir.

## R4 · Errores y reintentos

`errores_accionables.md` documenta los errores E-1, E-2 y E-3 del mazo con categoría, causa, camino de salida ejecutable y política decisiva. Cuando el material no especifica campos (E-1 y E-2), se explicita el supuesto didáctico. También se analiza el error real `invalid_idempotency_key`. El arnés en s05/engine.py registra la tupla canónica de llamadas fallidas y corta repeticiones idénticas devolviendo `repeated_failed_call` antes de ejecutar.

## R5 · Capacidades y tríada letal

El «sobre» de cinco capacidades **no fue proporcionado** por el profesor. Se construye un escenario hipotético **no oficial** en escenario_servidor_simulado.json, sin atribuirlo al material docente. La política distingue candidato meramente simulado de autorizaciones reales: default deny y server_allowlist vacía. Las dos capacidades innecesarias se excluyen; la descripción con instrucción incrustada entra a cuarentena **antes** de registrar/invocar; el efecto no declarado se deniega. La compuerta posterior verifica esquema, instrucciones, relevancia/frescura y efectos, y ante fallo dispone cuarentena/abstención. No se abre ninguna conexión MCP.

`inventario_triada.md` contiene seis flujos, las tres respuestas sí/no y la pata eliminada mediante controles explícitos, incluidos los flujos internos sin conexión externa.

## Ejecución verificada

GitHub Actions `validate-s05`, ejecución https://github.com/andres-alvarez19/S05_alvarez/actions/runs/38484917942, Python 3.12.15. Salida literal del ejecutor JSONL:

```text
PASS LECTURA_ERROR: contrato y expectativa verificados
PASS LECTURA_EXITO: contrato y expectativa verificados
PASS LECTURA_LIMITE: contrato y expectativa verificados
PASS ESCRITURA_ERROR: contrato y expectativa verificados
PASS ESCRITURA_EXITO: contrato y expectativa verificados
PASS ESCRITURA_LIMITE: contrato y expectativa verificados
RESULTADO: 6/6 casos válidos
```

Salida literal de `python -m pytest -q`:

```text
............                                                             [100%]
12 passed in 0.30s
```

La batería incluye aserción de detección del defecto sobre la ruta real `target_demo.converter.convert`. El ejemplo objetivo de laboratorio **contiene deliberadamente el defecto**; el runner de prueba generado falla por aserción, y la prueba del sistema verifica explícitamente ese fallo esperado. No se incluye dicho test generado como falla inesperada de la batería principal.

## Estado de entrega

**Entrega técnica preparada para presentar con salvedades:** las pruebas automatizadas y los entregables implementados están documentados; **R3 (revisión cruzada humana) no se realizó** por no conseguir contraparte, por lo que no puede considerarse requisito cumplido. El caso de cinco capacidades de R5 es hipotético por ausencia de material oficial, identificado expresamente en README. El cumplimiento total y cualquier descuento dependen de la evaluación docente.
