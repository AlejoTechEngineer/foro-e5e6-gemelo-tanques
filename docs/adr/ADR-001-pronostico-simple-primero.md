# ADR-001 — Pronóstico simple primero; el aprendizaje profundo se pospone

**Estado:** Aceptada · **Contexto:** El tiempo hasta el 90 % de un tanque depende casi por completo de un balance de masa
(capacidad, caudal de entrada). Los eventos de desborde son raros (decenas por semestre), y no existen aún etiquetas ni
series históricas continuas. Choi et al. (2021) revisan modelos profundos para anomalías multivariadas, pero esos modelos
requieren datos abundantes.

**Decisión:** (1) usar el **balance de masa** como referencia y modelo de contraste; (2) adoptar **suavizado exponencial de
Holt** sobre las lecturas del sensor como pronosticador operativo; (3) detectar anomalías con el **residuo** entre lo
observado y el balance; (4) reevaluar modelos profundos cuando haya un volumen de datos que lo justifique.

**Consecuencias:** `+` explicable ante el operario, `+` poco costo, `+` cumple "comparar contra referencia simple"
(Hyndman & Athanasopoulos, 2021). `−` limitada si hay dinámicas no lineales (p. ej. válvulas con histéresis).

**Evidencia en el repo:** `reports/resumen_resultados.md`, §4: Holt supera al balance en el conjunto de prueba; la regresión
móvil no siempre lo hace (se reporta).
