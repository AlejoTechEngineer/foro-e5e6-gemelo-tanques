# Foro Escenarios 5 y 6 — Pregunta e hipótesis del caso (Metodología de Casos)

**Caso:** desbordes de agua en tanques interconectados con llenado manual — planta textil, Bogotá (organización en reserva).
**Entrega:** foro analítico/argumentativo, Maestría en IA y Maestría en Arquitectura de Software (docente: María Cruz), 150 puntos.

Este repositorio convierte el borrador del grupo en un paquete completo y verificable:

1. **La publicación lista para pegar** (`docs/01_publicacion_foro.md`, 786 palabras sin referencias).
2. **El respaldo metodológico** de los Temas 5 y 6 (`docs/03`, `docs/04`).
3. **Un gemelo de simulación reproducible** que valida el protocolo de análisis y explora el diseño de la solución.
4. **Herramientas para la Parte 2** (respuestas individuales): plantilla, lista de coherencia, banco de aportes (`docs/02`).

> ### ⚠️ Integridad de los datos
> Los datos de `data/sintetico/` y los resultados de `reports/` son **sintéticos**. Las capacidades de los tanques,
> los llenados por mes y el comportamiento del operario son **supuestos** (marcados en `config/escenario_base.yaml`);
> solo los caudales y las frecuencias de desborde provienen del caso. Los números sirven para **validar el protocolo y el
> diseño**, no son hallazgos y **no deben citarse como evidencia** ante la docente.

## Qué cambió respecto al borrador original

| Punto | Borrador | Esta versión | Motivo |
|---|---|---|---|
| Naturaleza de las hipótesis | Diagnósticas (causas del desborde) | **Sobre la implementación de una solución** (aviso predictivo); las diagnósticas pasan a ser D1/D2 de la línea base | La rúbrica pide "hipótesis sobre la implementación de una posible solución" |
| Pregunta | Dos preguntas en una (factores + por qué varía) | Una pregunta que enlaza factores y eficacia del aviso | Concisión |
| Fuentes | 4, con descripciones | Las mismas 4, **con DOI/datos verificados** y "qué aporta" explícito | Rúbrica: discutir lo que aportan |
| Redacción de H1 | Texto confuso sobre la "salida detenida" | Definición operativa del margen de reacción | Claridad |
| Evidencia | Solo diario de campo | + registro de avisos, entrevistas y grupo focal | Mixto, según Temas 5 y 6 |
| Longitud | No verificada | 600–900 palabras, verificada por script | Rúbrica |

## Inicio rápido

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest                      # 22 pruebas
python -m gemelo_tanques    # regenera reports/ y data/sintetico/ (semilla 2026)
make words                  # cuenta palabras de la publicación
```

## Estructura

```
config/escenario_base.yaml     parámetros; cada dato marcado como "caso" o "supuesto"
src/gemelo_tanques/
  balance.py                   margen de reacción por balance de masa
  simulation.py                simulador con números aleatorios comunes (manual vs. predictivo)
  forecasting.py               pronóstico del tiempo a objetivo; partición temporal; referencia simple
  alarms.py                    carga de alarmas (inspirado en ISA-18.2)
  analysis.py                  Fisher, riesgo relativo, McNemar, logit, tamaño de muestra
  report.py / cli.py           figuras y resumen automático
tests/                         22 pruebas (calibración contra el caso, criterio de descarte, reproducibilidad…)
data/plantillas/               registro de llenados y diccionario de datos (para el diario de campo real)
docs/                          publicación, respuestas, metodología, matriz de coherencia, rúbrica, arquitectura, ADR
reports/                       resumen_resultados.md, figuras y CSV generados
```

## Lo que muestra la simulación (con las salvedades de arriba)

- El modo manual calibrado reproduce las frecuencias del caso (`reports/calibracion.csv`).
- El margen de reacción por balance ordena los tanques como el caso: Calderas y Compresores (~5 min) < Principal (8) < Auxiliar (12).
- **Un aviso sin antelación suficiente no ayuda** (con 0–1 min es igual o peor que operar manual) y **su eficacia depende
  tanto de que se perciba como de cuándo suena**: hallazgos de diseño que respaldan H2 y la recomendación de canal redundante.
- Pronosticar con un balance simple es competitivo; el suavizado de Holt lo mejora. La regresión móvil no siempre.
- Detectar una reducción del 75 % de desbordes exige del orden de cientos de llenados por fase: el piloto debe durar meses.

## Limitaciones

Capacidades y volúmenes supuestos · un solo sitio · D1 confundida con el tanque · Auxiliar sin potencia estadística ·
la referencia de carga de alarmas (≤ 1 por 10 min) proviene de la práctica citada en la literatura (EEMUA 191) y debe
verificarse en la norma ISA-18.2 antes de citarse formalmente · el enlace de ISA-18.2 apunta a la tienda de la norma.

## Citar y licencia

Código bajo licencia MIT (`LICENSE`). Referencias de la publicación en `docs/01_publicacion_foro.md`.
