# S05 — Auditoría del pañol

Entrega individual de Semana 5, continuando la fábrica T1 de [S03](https://github.com/andres-alvarez19/S03_Alvarez) y el arnés de [S04](https://github.com/andres-alvarez19/S04_Alvarez).

## Advertencia sobre la ronda 5: material no proporcionado

La guía de actividad indica que el profesor entregaría un **sobre con cinco capacidades de un servidor externo**. **Ese catálogo no fue proporcionado.** Para permitir desarrollar la práctica se creó un **escenario hipotético propio**, documentado en `escenario_servidor_simulado.json`. **No es material oficial ni evidencia de haber recibido las capacidades del profesor.** Los nombres, versiones y descripciones son ficticios, no corresponden a un servidor MCP operativo. Si posteriormente se entrega el catálogo oficial, deben sustituirse los supuestos y rehacerse la auditoría.

La política `politica_capacidades.json` utiliza **default-deny**; distingue análisis de la simulación de permisos efectivos. No se ejecuta ninguna conexión externa. El control `no_instruction_override` debe aplicarse también a **descripciones de herramientas antes de invocarlas**, no solo a las respuestas.

## Escenario simulado

| Capacidad | Hallazgo | Decisión |
| --- | --- | --- |
| `fetch_issue` | Lectura acotada de un caso por identificador | Elegible únicamente en la simulación, sin conexión real |
| `search_code` | Instrucción incrustada en su descripción (prompt injection) | Cuarentena; no permitir |
| `publish_report` | Declara lectura, pero tiene efecto de publicación | Denegar por efecto no declarado |
| `export_secrets` | No necesaria; expone secretos | Excluir |
| `run_shell` | No necesaria; ejecución arbitraria | Excluir |

## Estado de la entrega

- [x] Escenario externo hipotético documentado y claramente identificado.
- [x] Política JSON para las cinco capacidades simuladas.
- [ ] Auditoría del catálogo sembrado con ≥5 defectos y rediseño.
- [ ] Dos fichas de herramientas, contratos JSON Schema y seis pruebas ejecutables.
- [ ] Tres errores reescritos, un error propio y prevención de reintentos repetidos.
- [ ] Inventario de tríada letal de todos los flujos y evidencia de controles.
- [ ] Evidencia de ejecución real en `bitacora.md`.
- [ ] Auditoría cruzada de las herramientas de un compañero (pendiente por acuerdo).

**Importante:** esta incorporación resuelve la ausencia de material para *practicar* R5, pero **no equivale a completar toda la entrega S05** ni garantiza aceptación académica como sustituto del sobre original.
