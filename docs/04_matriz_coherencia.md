# Matriz de coherencia: problema → pregunta → hipótesis → variables → evidencia

La rúbrica valora (y las réplicas a otros grupos pueden usar) la **coherencia** entre estos cinco eslabones.

| Eslabón | Contenido | Verificación |
|---|---|---|
| Problema | 4–7 desbordes/mes por llenado manual sin alarma | Tiene indicador (frecuencia mensual) y datos por tanque |
| Fuente → componente | Ghorbani Bam (monitoreo) → sensor de nivel continuo · Choi (anomalías multivariadas) → detección de subidas anómalas · Hyndman (pronóstico + referencia simple) → modelo de tiempo a rebose · ISA-18.2 → alarma oportuna y no saturante | Cada fuente "aporta" algo concreto al diseño |
| Pregunta | Factores que determinan los desbordes y cómo condicionan la eficacia del aviso | No es sí/no, no plantea dilema, no pregunta por el futuro |
| H1 | VI: modo (manual/aviso) × margen → VD: proporción con desborde | Evidencia cuantitativa disponible tras el piloto |
| H2 | VI: antelación → VD: proporción con desborde | Evidencia cuantitativa + cualitativa |
| Hipótesis de diagnóstico D1, D2 (línea base) | D1: margen → desborde · D2: atención → desborde (criterio de descarte propio) | Se prueban con el diario de campo **antes** de instalar nada |

## Puntos débiles conocidos (para ser honestos en el foro)

1. **D1 y el tanque están confundidos** (ver `03`, validez interna): con cuatro tanques, el margen casi no varía dentro de uno.
2. **Auxiliar** (1–2 eventos/año) no admite inferencia estadística.
3. **Las capacidades y llenados/mes son supuestos** en este repositorio: hay que reemplazarlos con datos de planta.
4. **H1 y H2 comparten la VD** (proporción con desborde). Es deliberado — H1 compara *modos*, H2 compara
   *configuraciones* del mismo aviso — pero un evaluador podría preguntarlo.
5. **La H2 depende de medir el tiempo de respuesta**, que el sistema de avisos debe registrar desde el día 1 del piloto.
