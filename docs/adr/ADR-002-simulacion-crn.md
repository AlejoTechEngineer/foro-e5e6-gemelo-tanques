# ADR-002 — Gemelo de simulación con números aleatorios comunes (CRN)

**Estado:** Aceptada · **Contexto:** Se necesita validar el protocolo estadístico y explorar el espacio de diseño de la solución
(antelación, probabilidad de acuse) antes de tener datos de campo ni autorización de piloto.

**Decisión:** Un simulador Monte Carlo que genera, por llenado, todas las fuentes de azar **una sola vez** y luego aplica el modo
`manual` o `predictivo`. Esto permite comparaciones **pareadas** (McNemar) en simulación y, a la vez, reproducir el diseño
**no pareado** que tendrá el piloto real. Se calibra el modo manual con los rangos de desbordes del caso.

**Consecuencias:** `+` reproducible (semilla), `+` aísla el efecto de la intervención, `+` permite análisis de sensibilidad y de potencia.
`−` **los resultados dependen de supuestos** (capacidades, llenados/mes, distribuciones de retraso). Por eso toda salida lleva la
advertencia "DATOS SINTÉTICOS" y no puede citarse como evidencia del caso.
