# S05 · Auditoría del pañol — fábrica agéntica T1

Entrega individual de Semana 5, en continuidad con [S03](https://github.com/andres-alvarez19/S03_Alvarez) (informe de defecto → prueba ejecutable) y [S04](https://github.com/andres-alvarez19/S04_Alvarez) (arnés, permisos, traza, aislamiento). Esta entrega aplica contratos nuevos sin alterar aquellos repositorios.

## Aclaración indispensable: servidor externo no proporcionado

**El profesor no facilitó el «sobre cerrado» con cinco capacidades externas anunciado en la ronda 5.** Se creó un **escenario hipotético propio, identificado como SIMULADO_NO_OFICIAL**, en `escenario_servidor_simulado.json`. **No es un servidor MCP real ni el catálogo oficial; no debe atribuirse al profesor.** Permite practicar la auditoría de cinco capacidades pero su aceptación como sustitución del material oficial es decisión docente.

Las cinco capacidades ilustrativas son:
- `fetch_issue`: lectura necesaria, **candidata simulada**, no autorización real.
- `search_code`: instrucción incrustada en la descripción; **cuarentena antes de invocación**.
- `publish_report`: declara lectura pero publica; **denegada por efecto no declarado**.
- `export_secrets`: innecesaria; **excluida**.
- `run_shell`: innecesaria; **excluida**.

La política `politica_capacidades.json` tiene **default deny**, versiones simuladas fijadas, controles de pre-gate y post-gate, permisos candidatos por componente y conducta `quarantine_and_abstain`. La autorización operativa es vacía: `server_allowlist=[]` y `operational_external_access=false`. Ninguna operación externa se ejecuta.

## Archivos para la entrega

| Evidencia | Archivos | Estado |
|---|---|---|
| R1: auditoría de doce puntos, siete hallazgos, rediseño a tres | `auditoria.md` | Completa |
| R2: dos fichas YAML, schemas, manifiesto y seis casos JSONL | `tools/`, `schemas/tools/`, `evals/tools/` | Completa |
| R3: auditoría cruzada ajena y revisión recibida | plantilla en `auditoria.md` | **Pendiente de compañero** |
| R4: tres errores del mazo, uno propio y bloqueo de reintento repetido | `errores_accionables.md`, `s05/engine.py` | Completa |
| R5: política externa simulada e inventario de tríada letal | `politica_capacidades.json`, `inventario_triada.md` | Completa con salvedad |
| Bitácora y pruebas | `bitacora.md`, `evidence/tests.txt` | Verificadas |

### Herramientas construidas

`consultar_informes_defecto` es de lectura: retorna entre cero y tres informes por página, con límite por defecto 2 y cinco metadatos obligatorios. `registrar_prueba_defecto` es de escritura: crea una prueba pytest en `WORK/tests` para DEF-001, con clave `report_id:case_id`, efecto write-once, replay idempotente y vista previa acotada. Están separadas en permisos del manifiesto `tools/tools.manifest.json`. Los schemas llevan validación estricta y `additionalProperties: false`.

DEF-001 procede del informe fuente de la fábrica anterior. DEF-002 y DEF-003 están identificados como **sintéticos**, exclusivamente para la evaluación de paginación. `target_demo/converter.py` contiene deliberadamente el defecto DEF-001; el caso pytest generado debe **fallar por aserción verificable**, y una prueba de la batería comprueba precisamente ese fallo esperado. No se ejecuta código de producción real.

### Ejecutar validaciones

Python 3.12:

```bash
python -m pip install -r requirements.txt
python scripts/run_tool_evals.py
python -m pytest -q
```

Las seis pruebas JSONL se ejecutan en directorios temporales, sin alterar INPUT ni OUTPUT. El workflow `.github/workflows/validate.yml` ejecuta los mismos comandos tras cada push.

**Evidencia confirmada por GitHub Actions:** [ejecución de validación](https://github.com/andres-alvarez19/S05_alvarez/actions/runs/38484917942), `RESULTADO: 6/6 casos válidos`; `12 passed in 0.30s`. La salida se conserva literalmente en `bitacora.md`.

## Paso pendiente: auditoría cruzada

Entregar a un compañero las dos fichas de `tools/` junto al manifiesto y schemas referenciados. Solicitar su catálogo; sin pedir explicaciones, resolver en `auditoria.md` los tres escenarios de la consigna y un hallazgo concreto del punto 11 o 12 con consecuencia y corrección. Incorporar también la revisión del compañero sobre nuestro catálogo. No se inventan auditorías externas. **La actividad está lista para ese intercambio, no completamente cerrada hasta recibirlo.**

## Límite de seguridad del laboratorio

Las herramientas operan con permisos lógicos dentro de la práctica. La falta de conectividad externa y el confinamiento de producción requieren controles adicionales de infraestructura en un despliegue real. El servidor de cinco capacidades está simulado, no conectado.
