# R5 · Inventario de tríada letal de los flujos T1

Las tres condiciones son (1) acceso a datos sensibles/internos, (2) contenido bajo control de terceros, (3) canal de salida externa. No basta con un aviso si se cumplen las tres: hay que eliminar al menos una. La salida a WORK/tests es **interna**, no un canal de exfiltración por sí misma.

| Flujo | ¿Datos sensibles? | ¿Contenido de terceros? | ¿Canal de salida? | Pata que elimino y cómo |
|---|:---:|:---:|:---:|---|
| Informe INPUT/raw → consultar_informes_defecto | Sí | Sí | No | **Canal de salida externa:** consulta local read_only, sin red; resultados acotados |
| Informe → registrar_prueba_defecto → WORK/tests | Sí | Sí | No | **Canal de salida externa:** escritura confinada a WORK; no publica ni transmite |
| Prueba generada → pytest local sobre target_demo | Sí | Sí | No | **Canal de salida externa:** se prueba objetivo determinista local, sin contenido ejecutable arbitrario de informes |
| Descripciones del servidor hipotético → análisis de pre-gate | No | Sí | No | **Acceso a datos internos:** análisis estático sin exponer INPUT; toda conexión operativa denegada |
| Descripción con instrucción incrustada → cuarentena | No | Sí | No | **Acceso a datos y salida externa:** se rechaza en descripción ANTES del registro, sin ejecutar acción |
| Respuesta hipotética externa → post-gate | No | Sí | No | **Canal de salida externa:** no hay conexión; esquema, relevancia, efectos y override se controlan; cuarentena si falla |

**Escenario R5 no oficial:** El profesor no entregó el catálogo prometido. Se desarrolló `escenario_servidor_simulado.json` como ejercicio sustitutivo explícito. De cinco capacidades, `export_secrets` y `run_shell` son innecesarias; `publish_report` oculta un efecto, `search_code` contiene instrucción en su descripción y entra a cuarentena previa; `fetch_issue` es solo candidata ficticia, no permiso real.

**Política efectiva:** `politica_capacidades.json` configura `default=deny`, `server_allowlist=[]`, `operational_external_access=false`; el ensayo de permisos `simulated_candidate_allowlist` no autoriza ninguna operación real. Los controles de sandbox/red en producción requieren mecanismos de infraestructura adicionales.
