# Resultados de la simulación (DATOS SINTÉTICOS)

> **Advertencia de integridad.** Estos resultados provienen de un modelo con supuestos (capacidades, llenados/mes, comportamiento del operario) calibrado únicamente con los rangos de desbordes del caso. **No son evidencia empírica** ni deben citarse como hallazgos. Validan el *protocolo de análisis* y el *diseño de la solución* antes del piloto.

Semilla: `2026` · Horizonte: 6 meses · Antelación base del aviso: 6 min

## 1. Margen de reacción por balance (variable de la H1 diagnóstica)

| tanque      |   capacidad_m3_supuesta |   caudal_min_m3h |   caudal_max_m3h |   margen_min_conservador |   margen_min_nominal |   margen_min_optimista |
|:------------|------------------------:|-----------------:|-----------------:|-------------------------:|---------------------:|-----------------------:|
| calderas    |                      30 |               30 |               35 |                     5.14 |                 5.54 |                      6 |
| compresores |                      40 |               40 |               45 |                     5.33 |                 5.65 |                      6 |
| principal   |                     120 |               90 |               90 |                     8    |                 8    |                      8 |
| auxiliar    |                      10 |                5 |                5 |                    12    |                12    |                     12 |

## 2. Calibración del modo manual (240 meses simulados vs. rangos del caso)

| tanque      |   llenados |   desbordes_por_mes |   proporcion_desborde |   observado_min |   observado_max | dentro_de_rango   |
|:------------|-----------:|--------------------:|----------------------:|----------------:|----------------:|:------------------|
| auxiliar    |       4728 |              0.0958 |                0.0049 |           0.083 |           0.167 | True              |
| calderas    |      14384 |              2.45   |                0.0409 |           2     |           3     | True              |
| compresores |      14478 |              2.4208 |                0.0401 |           2     |           3     | True              |
| principal   |       7212 |              0.5417 |                0.018  |           0     |           1     | True              |

## 3. Diagnóstico con la línea base manual (6 meses)

| tanque      |   llenados |   desbordes |   margen_medio_min |   volumen_desbordado_m3 |   proporcion |   ic95_inf |   ic95_sup |
|:------------|-----------:|------------:|-------------------:|------------------------:|-------------:|-----------:|-----------:|
| calderas    |        374 |          18 |              5.543 |                  20.161 |        0.048 |      0.031 |      0.075 |
| compresores |        366 |          15 |              5.647 |                  28.82  |        0.041 |      0.025 |      0.067 |
| principal   |        158 |           4 |              8     |                   6.75  |        0.025 |      0.01  |      0.063 |
| auxiliar    |        108 |           0 |             12     |                   0     |        0     |      0     |      0.034 |

- **D1 (margen → desborde):** OR por minuto de margen = 0.68 (IC95 % 0.48–0.95; p = 0.0249). *Limitación:* el margen varía sobre todo **entre** tanques, de modo que D1 está confundida con características propias de cada tanque (ver `docs/03`, validez interna).
- **D2 (atención → desborde):** p(vigilancia) = 0.000; p(otra actividad) = 0.088; Fisher p = 4.2e-15. Decisión con el criterio de descarte del grupo: **SOSTENIDA (p<0,05)**.

## 4. Pronóstico del tiempo hasta el 90 % (conjunto de prueba)

Hiperparámetros ajustados solo con la primera mitad: {'ventana_min': 5, 'alpha': 0.1, 'beta': 0.02}.

|   horizonte_min | metodo   |   n |   sesgo_min |   mae_min |   rmse_min |
|----------------:|:---------|----:|------------:|----------:|-----------:|
|               3 | balance  | 120 |      -0.054 |     0.296 |      0.386 |
|               3 | holt     | 120 |      -0.042 |     0.114 |      0.138 |
|               3 | ols      | 120 |      -0.064 |     0.23  |      0.303 |
|               5 | balance  | 120 |      -0.038 |     0.345 |      0.439 |
|               5 | holt     | 120 |       0.006 |     0.147 |      0.189 |
|               5 | ols      | 120 |      -0.004 |     0.33  |      0.457 |
|              10 | balance  | 120 |      -0.033 |     0.365 |      0.479 |
|              10 | holt     | 120 |       0.166 |     0.329 |      0.402 |
|              10 | ols      | 120 |      -0.069 |     0.469 |      0.613 |

Lectura (calculada): a 3 min gana holt (RMSE 0.14 vs. 0.39 del balance); a 5 min gana holt (RMSE 0.19 vs. 0.44 del balance); a 10 min gana holt (RMSE 0.40 vs. 0.48 del balance). Empeoran la referencia: ols a 5 min, ols a 10 min. Se reporta tal cual: Hyndman & Athanasopoulos (2021) exigen comparar contra referencias simples.

## 5. H1 (solución): aviso predictivo vs. manual — diseño antes/después no pareado

| tanque      |   llenados |   desbordes |   margen_medio_min |   volumen_desbordado_m3 |   proporcion |   ic95_inf |   ic95_sup |
|:------------|-----------:|------------:|-------------------:|------------------------:|-------------:|-----------:|-----------:|
| calderas    |        387 |           9 |              5.548 |                  21.97  |        0.023 |      0.012 |      0.044 |
| compresores |        373 |           5 |              5.644 |                  17.066 |        0.013 |      0.006 |      0.031 |
| principal   |        190 |           2 |              8     |                   7.841 |        0.011 |      0.003 |      0.038 |
| auxiliar    |        101 |           1 |             12     |                   0.213 |        0.01  |      0.002 |      0.054 |

- Global: 3.68 % → 1.62 % (reducción absoluta 2.06 pp; IC95 % bootstrap 0.69–3.44; RR = 0.44, IC95 % 0.23–0.75; Fisher p = 0.0036).
  - auxiliar: 0.00 % → 0.99 % (reducción absoluta -0.99 pp)
  - calderas: 4.81 % → 2.33 % (reducción absoluta 2.49 pp)
  - compresores: 4.10 % → 1.34 % (reducción absoluta 2.76 pp)
  - principal: 2.53 % → 1.05 % (reducción absoluta 1.48 pp)
- Comparación pareada (mismo azar): desbordan solo en manual = 29, solo en predictivo = 8; McNemar exacto p = 0.00075. *Solo posible en simulación; el piloto real será no pareado.*

## 6. Carga de alarmas (inspirada en ISA-18.2)

- Avisos/día: 5.6; por 10 min: media 0.039, p99 1, máx. 3. ¿Bajo la referencia de 1/10 min? **Sí**.
- Avisos decisivos (habrían desbordado sin aviso): 2.9 %. El resto son avisos rutinarios: bajo carga, pero cabe vigilar la fatiga si se añaden más tanques.

## 7. H2: antelación del aviso

P90 del tiempo de respuesta cuando el operario está en otra actividad ≈ 7.3 min. Línea base manual: 3.23 % de llenados con desborde.

|   p_acuse_otra |   antelacion_min |   proporcion_desborde |   pct_a_tiempo_acusados |
|---------------:|-----------------:|----------------------:|------------------------:|
|           0.85 |                0 |                0.0542 |                  0.9473 |
|           0.85 |                1 |                0.0414 |                  0.961  |
|           0.85 |                2 |                0.0314 |                  0.9718 |
|           0.85 |                3 |                0.0242 |                  0.9795 |
|           0.85 |                4 |                0.019  |                  0.9851 |
|           0.85 |                6 |                0.0131 |                  0.9914 |
|           0.85 |                8 |                0.0095 |                  0.9954 |
|           0.85 |               10 |                0.0077 |                  0.9973 |
|           0.85 |               12 |                0.0066 |                  0.9984 |

Lectura (calculada): con antelación ≤ 1 min el aviso NO mejora la operación manual; la supera desde 2 min; ≥ 99 % de los avisos acusados se atienden a tiempo desde 6 min (P90 de respuesta ≈ 7.3 min). Es consecuencia del modelo y sus supuestos, no un hallazgo del caso.

## 8. Tamaño de muestra del piloto

Con p base ≈ 3.23 %, detectar una reducción del 75 % requiere ≈ 477 llenados por grupo y del 50 %, ≈ 1382 (α = 0,05; potencia 0,80). Con ≈ 170 llenados/mes (supuesto), esto equivale a varios meses por fase.
