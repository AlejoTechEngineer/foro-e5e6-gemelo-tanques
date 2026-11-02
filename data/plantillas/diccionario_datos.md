# Diccionario del "registro común" (diario de campo)

Se registran **todos** los llenados, no solo los que terminan en desborde (el denominador es
indispensable para calcular proporciones). Un renglón = un llenado.

| Campo | Tipo | Cómo se mide / valores | Hipótesis que lo usa |
|---|---|---|---|
| `llenado_id` | entero | consecutivo | todas |
| `fecha`, `hora` | AAAA-MM-DD, HH:MM | inicio del llenado (reloj de planta) | todas |
| `tanque` | cat. | `auxiliar`, `calderas`, `compresores`, `principal` | todas |
| `atencion` | cat. | `vigilancia` (observa el tanque) / `otra_actividad` (atiende otra tarea) al llegar al 90 % | D2, H1 (mod.) |
| `caudal_entrada_m3h` | real | del medidor, o por balance de las válvulas abiertas | D1 |
| `modo` | cat. | `manual` (línea base) / `predictivo` (piloto) | H1 |
| `aviso_acusado` | 0/1 | el operario reconoció el aviso (solo `predictivo`) | H2 |
| `t_respuesta_min` | real | minutos entre el aviso y el cierre de la válvula | H2 |
| `desborde` | 0/1 | hubo rebose visible o detectado por el sensor de alto-alto | todas |
| `duracion_desborde_min` | real | duración aproximada del rebose | indicadores |
| `volumen_desbordado_m3` | real | estimado = duración × caudal de entrada | indicadores |
| `observaciones` | texto | contexto cualitativo (p. ej. consumo atípico, falla de válvula) | triangulación |

**Margen de reacción** (no se registra; se calcula): `0,10 × capacidad / caudal_entrada × 60` (min), con la
transferencia de salida detenida. Requiere las capacidades reales de los tanques (en este repositorio
son supuestos).
