<!-- Copiar y pegar en el foro. Completar los corchetes. Verificar longitud: `make words`. -->

**Grupo [8]** — [Nombres de todos los integrantes]

**Caso y organización:** Desbordes de agua en tanques interconectados — manufactura textil, Bogotá (el nombre de la organización se mantiene en reserva por solicitud de la empresa).

## 1. Problema

El llenado de cuatro tanques interconectados (Auxiliar, Calderas, Compresores y Principal) se controla de forma manual: el operario abre y cierra válvulas, y no existe corte automático ni alarma de alto nivel. En seis meses de observación en 2026 se registraron entre 4 y 7 desbordes al mes (48 a 84 al año). El indicador es la frecuencia mensual de desbordes por tanque: Calderas y Compresores desbordan entre 2 y 3 veces al mes cada uno, Principal entre 0 y 1, y Auxiliar entre 1 y 2 al año.

## 2. Antecedentes: las cuatro fuentes

**Fuentes académicas**

1. **Ghorbani Bam et al. (2025)** revisaron 147 estudios sobre gemelos digitales en el sector del agua y encontraron que permiten monitoreo en tiempo real, simulación y control predictivo, aunque su adopción sigue siendo emergente. *Aporta:* medir niveles y eventos de forma continua es la base para calcular la frecuencia y el volumen de los desbordes. DOI: https://doi.org/10.3390/w17202957

2. **Choi et al. (2021)** revisaron métodos de aprendizaje profundo para detectar anomalías en series de tiempo y compararon modelos recientes sobre conjuntos de datos de referencia; hallaron que en series multivariadas hay que considerar a la vez la dependencia temporal y la relación entre variables. *Aporta:* orienta el componente que detectaría subidas anómalas de nivel, que dependen a la vez del nivel, los caudales de entrada y los consumos de cada tanque. DOI: https://doi.org/10.1109/ACCESS.2021.3107975

**Fuentes técnicas**

3. **Hyndman y Athanasopoulos (2021)**, texto abierto de pronóstico, presentan desde el suavizado exponencial y ARIMA hasta modelos con variables explicativas, y establecen que un pronóstico se evalúa con datos no usados para ajustarlo y se compara con métodos de referencia simples. *Aporta:* guía el modelo que estimaría el tiempo que falta para el rebose de cada tanque y obliga a compararlo con una referencia simple, el balance de masa. Enlace: https://otexts.com/fpp3/

4. **ISA (2016), ANSI/ISA-18.2**, norma de gestión de alarmas en la industria de procesos, define su ciclo de vida y entiende la alarma como un aviso al operador sobre una condición anormal que exige respuesta oportuna. *Aporta:* el aviso del modelo debe llegar con tiempo para que el operario actúe, sin saturarlo con avisos innecesarios. Enlace: https://www.isa.org/store/products/product-detail/?productId=46961965

## 3. Pregunta de investigación

¿Qué factores operativos y técnicos determinan la frecuencia de desbordes de cada tanque interconectado y cómo condicionan la eficacia de un aviso predictivo de nivel para el operario?

## 4. Hipótesis sobre la implementación de la solución

La solución propuesta es un aviso predictivo: a partir de lecturas continuas de nivel, se estima cuántos minutos faltan para que el tanque llegue al 90 % y se avisa al operario con una antelación configurable.

**H1. Aviso predictivo y desbordes.** Frente al llenado manual actual, el aviso predictivo reduce la proporción de llenados que terminan en desborde, y la reducción absoluta es mayor en los tanques con menor margen de reacción (Calderas y Compresores) que en Principal y Auxiliar.
- *Variable independiente:* modo de operación (manual / con aviso predictivo), moderada por el margen de reacción del tanque, es decir, el tiempo que tarda en llenar su último 10 % con la transferencia de salida detenida, calculado por balance con capacidad, entradas y consumos.
- *Variable dependiente:* proporción de llenados con desborde, por tanque.
- *Evidencia (cuantitativa):* registro de todos los llenados (fecha, hora, tanque, atención del operario, duración aproximada del desborde) en una línea base manual y en un piloto con aviso; comparación de proporciones antes y después por tanque. Se descarta H1 si en Calderas y Compresores la proporción con aviso no es menor que la manual.

**H2. Antelación del aviso y respuesta oportuna.** Los llenados cuyo aviso llega con una antelación mayor al percentil 90 del tiempo de respuesta del operario terminan en desborde en menor proporción que los de antelación menor.
- *Variable independiente:* antelación del aviso (minutos antes de alcanzar el 90 %), configurada en dos niveles durante el piloto.
- *Variable dependiente:* proporción de llenados con aviso que terminan en desborde.
- *Evidencia (cuantitativa y cualitativa):* registro de la hora del aviso, el reconocimiento y el cierre de la válvula; entrevistas semiestructuradas y un grupo focal con los operarios sobre claridad, carga y confianza en el aviso, con consentimiento informado.

Cada tanque se analiza como caso incrustado (Yin, 2018): los resultados permitirán identificar factores asociados a los desbordes en esta planta, pero no generalizarlos a otras. Antes del piloto, el grupo construyó un prototipo de simulación reproducible con datos sintéticos, para validar el protocolo de análisis; esos datos no constituyen evidencia del caso. [enlace al repositorio]

## Referencias

Choi, K., Yi, J., Park, C., & Yoon, S. (2021). Deep learning for anomaly detection in time-series data: Review, analysis, and guidelines. *IEEE Access, 9*, 120043–120065. https://doi.org/10.1109/ACCESS.2021.3107975

Ghorbani Bam, P., Rezaei, N., Roubanis, A., Austin, D., Austin, E., Tarroja, B., Takacs, I., Villez, K., & Rosso, D. (2025). Digital twin applications in the water sector: A review. *Water, 17*(20), Artículo 2957. https://doi.org/10.3390/w17202957

Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3rd ed.). OTexts. https://otexts.com/fpp3/

International Society of Automation. (2016). *Management of alarm systems for the process industries* (ANSI/ISA-18.2-2016). https://www.isa.org/store/products/product-detail/?productId=46961965

Yin, R. K. (2018). *Case study research and applications: Design and methods* (6th ed.). SAGE Publications.
