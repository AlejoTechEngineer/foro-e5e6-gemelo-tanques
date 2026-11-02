# Diseño metodológico y protocolo de campo

Aplica los Temas 5 y 6 del módulo. Es el respaldo detrás de la publicación: no hace falta pegarlo en el foro,
pero sustenta las hipótesis y sirve para las réplicas.

## 1. Tipo de estudio y unidad de análisis (Tema 5, §3; Yin, 2018)

- **Estudio de caso único con unidades incrustadas:** el sistema de tanques es el caso; cada tanque es una
  subunidad. Los resultados explican factores *en esta planta*; no se generalizan (Dul & Hak, 2008).
- **Enfoque mixto:** cuantitativo descriptivo/inferencial para magnitudes y proporciones (Tema 6) y cualitativo
  para el *porqué* del comportamiento del operario (Tema 5). La secuencia sigue la Figura 2 del Tema 5, con
  revisión de la problemática tras el análisis (los hallazgos pueden reformular D1/D2/H1/H2).

## 2. Protocolo: dimensión cognitiva y operativa (Tema 5, §2)

| Dimensión | Elemento | Estado |
|---|---|---|
| Cognitiva | Problema, pregunta, hipótesis, literatura | Ver `01_publicacion_foro.md` |
| Cognitiva | Instrumentos: registro común, guía de entrevista, hoja de observación | Secciones 5 y 6 de este documento |
| Operativa | **Aval escrito del representante legal** (el nombre de la empresa sigue en reserva) | Pendiente — precondición del trabajo de campo |
| Operativa | Visita, personas y recursos (cronómetro, planilla, acceso a planos/P&ID) | Por planificar |
| Ética | **Consentimiento informado** de cada operario antes de entrevistar o registrar; no divulgar nombres ni opiniones sin autorización expresa (Tema 5, §4.2) | Formato en la sección 6 |

Habilidades del investigador (Tema 5, Fig. 1): preguntas consistentes con el problema, escucha de las palabras
exactas de los entrevistados, adaptabilidad y **ausencia de sesgos** — en particular, no inducir al operario a
justificar los desbordes ni presentarlo como culpable: H2 mide un efecto *del diseño del trabajo*, no de la persona.

## 3. Secuencia de medición (Dul & Hak, 2008, p. 253, citado en Tema 6, §3)

| Paso | Desborde (VD) | Margen de reacción (VI/moderadora) | Atención del operario | Antelación y respuesta al aviso |
|---|---|---|---|---|
| 1. Definición precisa | Rebose de agua fuera del tanque, visible o detectado por sensor alto-alto | Min para llenar el último 10 % con la salida detenida | Estado al llegar al 90 %: vigilancia directa vs. otra actividad | Antelación = min entre aviso y 90 %; respuesta = min entre aviso y cierre |
| 2. Objeto de medida | Cada **llenado** (no el tanque) | Cada llenado, por tanque | Cada llenado | Cada aviso emitido |
| 3. Ubicación | Diario de campo; sensor alto-alto en el piloto | Planos, placas, medidores de caudal | Observación directa / planilla | Registro del sistema de avisos |
| 4. Extracción de evidencia | Observación o sensor | Cálculo por balance (`balance.py`) | Observador marca el estado | Marcas de tiempo del sistema |
| 5. Registro | `registro_llenados.csv` | Calculado, no registrado | Campo `atencion` | Campos `aviso_acusado`, `t_respuesta_min` |
| 6. Categorización | 0/1; duración y volumen | Continua (min) | Binaria | Continua; categoría ≥/< P90 |
| 7. Protocolo | `data/plantillas/diccionario_datos.md` | Parámetros en `config/` | Instructivo de observación (sec. 5) | Configuración de umbrales |

El **objeto de medida no es la unidad de análisis**: la unidad es el tanque; el objeto son los datos de cada llenado.

## 4. Muestra y tamaño (Tema 6, §2.1)

- **Muestreo no probabilístico por criterio**: se registran *todos* los llenados de un periodo (censo del periodo), no una
  muestra aleatoria; coherente con un caso único.
- Para el piloto, `analysis.tamano_muestra` estima los llenados por fase necesarios (α = 0,05; potencia 0,80). Con una
  proporción base de unos pocos por ciento, **detectar una reducción del 75 % exige del orden de cientos de llenados por
  fase** (ver `reports/resumen_resultados.md`, sec. 8). Auxiliar, con 1–2 desbordes/año, **no permite inferencia propia**:
  se reporta de forma descriptiva.
- Datos **longitudinales** (evolución mensual de desbordes) y **transversales** (comparación entre tanques) se
  presentan por separado.

## 5. Instrumentos de campo

**Hoja de observación directa (por llenado):** hora de inicio; tanque; válvulas abiertas; qué hace el operario a los 5 min
de alcanzar el 90 % (vigilando / otra tarea: ¿cuál?); hora de cierre; ¿hubo rebose?; duración aproximada; incidentes.

**Guía de entrevista semiestructurada (operarios; 30–40 min; Tema 5, §4.2):**
1. Contexto y propósito; confianza; consentimiento (sección 6).
2. Cuéntenos cómo es un llenado típico de Calderas, de principio a fin.
3. ¿Qué otras tareas compiten con la vigilancia del tanque en el mismo momento?
4. ¿Cómo se entera de que un tanque está por llenarse? ¿Qué señales usa hoy?
5. Describa la última vez que se rebosó un tanque. ¿Qué pasó antes, qué decidió y por qué?
6. (Piloto) ¿El aviso llegó a tiempo? ¿Cuántos avisos son demasiados? ¿Confía en lo que dice el aviso?
7. ¿Qué cambiaría del sistema para que usted pueda cerrar a tiempo?
8. Cierre y agradecimiento.

Ficha del entrevistado: rol, turno, antigüedad en el cargo (sin nombre en los resultados, salvo autorización).
**Grupo focal** (3 a 10 personas): una sesión tras el piloto para contrastar controversias y puntos en común.

## 6. Consentimiento informado (modelo)

> Entiendo que participo voluntariamente en un estudio académico sobre el llenado de tanques. Se me informó el propósito, que
> puedo retirarme cuando quiera, que la sesión será registrada (nota / audio) y que mi nombre y mis opiniones no se divulgarán
> sin mi autorización expresa. Firma: ____  Fecha: ____

## 7. Triangulación

Se contrastan tres fuentes: (a) el **diario de campo** (cuantitativo), (b) **documentos** de la planta (bitácoras de
mantenimiento, reportes de incidentes, facturas de agua) y (c) **entrevistas/grupo focal** (percepción). Una discrepancia
entre las tres (p. ej. el operario dice que "casi nunca" se rebosa, pero la bitácora muestra otra cosa) es un hallazgo en sí.

## 8. Criterios de validez (Escenario 3 / Lectura 2)

| Criterio | Amenaza concreta | Mitigación |
|---|---|---|
| **Constructo** | "Desborde" y "atención" mal definidos | Definiciones operativas (sec. 3); sensor alto-alto como verdad objetiva |
| **Interna** | D1 está **confundida con el tanque**: el margen varía casi solo entre tanques; efecto Hawthorne (el operario se comporta distinto al ser observado); cambios estacionales de consumo entre línea base y piloto | Comparar dentro de cada tanque (antes/después); registrar consumo; alternar configuraciones en el piloto; observación previa de habituación |
| **Externa** | Un solo sitio | No se generaliza; se declara explícitamente (Yin, 2018) |
| **Replicabilidad** | Procedimiento opaco | Este repositorio: parámetros, código, plantillas y semillas fijas |
