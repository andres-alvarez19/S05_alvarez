# Auditoría de catálogo — S05

## R1 · Lista de doce puntos sobre el catálogo sembrado

La tabla 5.0 de la guía solo proporciona siete nombres y descripciones, no esquemas, permisos ni implementaciones. **NV** significa «no verificable con la evidencia disponible», no un incumplimiento de código demostrado.

| Punto | Diagnóstico basado en la tabla |
|---|---|
| 1. Nombre con verbo, objeto y ámbito | No: H-1 a H-7 omiten ámbito inequívoco |
| 2. Primera frase dice qué devuelve | No: H-1, H-3, H-5, H-6 y H-7; H-2/H-4 sí describen devolución |
| 3. Cardinalidad explícita | No: H-1 y H-7; H-2/H-3 singular, H-4 plural |
| 4. Cuándo no usar y alternativa | No: ninguna lo declara |
| 5. Comportamientos por defecto declarados | No: H-7 promete consulta arbitraria; otros NV |
| 6. Enumeraciones, patrones, mínimos, máximos | NV, sin schemas de entrada |
| 7. additionalProperties false | NV, sin schemas de entrada |
| 8. Límite por defecto y máximo | No: H-4 y H-7 no acotan resultados; otros NV |
| 9. Total, truncado y cursor | No: H-4 promete «todos» sin metadatos; otros NV |
| 10. Error como dato, cuatro elementos | NV, sin contratos de error |
| 11. Escritura idempotente y separada | **NV a nivel catálogo**: H-5/H-6 no acreditan claves ni separación |
| 12. Sin solapamientos | **No a nivel catálogo**: H-2/H-3 y H-5/H-6 se solapan |

## Hallazgos con consecuencia y corrección

| Herramienta | Punto | Consecuencia concreta del defecto | Corrección propuesta |
|---|---|---|---|
| H-1 buscar_datos | 1,2,3,4 | Podría consultar datos incorrectos y no sabría si devuelve un registro o un conjunto | Renombrar a listar_casos con filtros, cardinalidad y paginación |
| H-2 obtener_registro | 4,12 | Compite con H-3 al consultar por ID, provocando elección arbitraria | Fusionar en obtener_caso |
| H-3 consultar_registro | 4,12 | Duplica H-2 y permite invocaciones redundantes | Eliminar y usar obtener_caso |
| H-4 listar_todo | 8,9 | Lista masiva saturaría el contexto; no puede distinguir muestra del total | listar_casos con page_size 20, máximo 100, total y cursor |
| H-5 actualizar_estado | 4,11,12 | Compite con cierre de H-6 y no acredita clave idempotente; riesgo en reintentos | cambiar_estado_caso con clave caso_id:estado_destino |
| H-6 cerrar_caso | 4,11,12 | «Ya no necesito ayuda» no distingue entre cerrar y actualizar estado | Absorber cierre en cambiar_estado_caso con estado_destino=cerrado |
| H-7 ejecutar_consulta | 1,4,5,8 | Consulta arbitraria sin límite ni alcance definido puede traer datos masivos o producir efectos inesperados | Retirar; solo consultas por ID y filtros acotados |

**Precisión:** en el punto 11 la ausencia de documentación no demuestra que una implementación duplique escrituras, pero sí impide certificar sus controles antes de registrarla. En el 12 la colisión entre disparadores es evidente.

## Catálogo rediseñado: tres herramientas (antes siete)

1. **obtener_caso:** lectura de un caso por ID; no usar para conjuntos.
2. **listar_casos:** lectura de 0..100 casos por página, 20 por defecto, filtros en la fuente, cursor y total; no usar para un ID único.
3. **cambiar_estado_caso:** única escritura, rol writer, clave caso_id:estado_destino, aprobación humana para efecto irreversible; nunca para lectura.

## Nuestras dos herramientas

**consultar_informes_defecto** devuelve colecciones paginadas y no escribe. **registrar_prueba_defecto** crea un artefacto pytest en WORK/tests de forma idempotente y no consulta. Disparadores diferenciados; permisos segregados en tools/tools.manifest.json. Evidencia para los doce puntos: fichas YAML, schemas, implementación y seis JSONL.

## R3 · Auditoría cruzada — PENDIENTE

No se ha recibido catálogo ajeno. Completar sin consultar a su autor:

| Escenario de la guía | Herramienta elegida | Justificación leyendo solo catálogo |
|---|---|---|
| Consultar por un identificador conocido | PENDIENTE | PENDIENTE |
| Consultar varios elementos que cumplen condición | PENDIENTE | PENDIENTE |
| Usuario: «ya no necesito ayuda» | PENDIENTE | PENDIENTE |

Hallazgo de conjunto de punto 11 o 12, consecuencia y corrección específica: **PENDIENTE**.
Retroalimentación de compañero sobre nuestro catálogo: **PENDIENTE**.
