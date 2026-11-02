# Parte 2 — Respuestas individuales (30 + 30 pts, plazo: 3 de noviembre, 23:55)

> No se pueden redactar respuestas útiles sin leer las publicaciones de los otros grupos. Este documento deja la
> **plantilla**, la **lista de verificación de coherencia** y un **banco de aportes** para producir dos respuestas de
> nivel *Excelente* en pocos minutos cuando se tenga el texto de cada grupo.

## 1. Qué cuenta como "Excelente" (30 pts)

Aporta **al menos uno** de: (a) fuente adicional pertinente con referencia; (b) experiencia personal/profesional similar
con **recomendación concreta**; (c) revisión de coherencia problema ↔ pregunta ↔ hipótesis ↔ evidencia. Lo ideal es
combinar (c) con (a) o (b). Una opinión general ("muy interesante") vale 10/30. Se recomienda responder al menos a un
grupo de la **otra maestría**.

## 2. Plantilla (120–200 palabras)

```
Grupo [N] — [Título del caso]. Gracias por compartir su publicación.

1) Lo que ya funciona: [una fortaleza específica, p. ej. "su indicador de latencia p95 hace falsable la H2"].

2) Coherencia: [señalar un eslabón débil con razón]. Por ejemplo: "La hipótesis [X] no se puede probar con
   los datos que mencionan porque [la variable dependiente no está registrada / el 'antes' no existe /
   la muestra es de [n] eventos]. Sugerimos [medida concreta]."

3) Aporte: [fuente adicional con referencia APA] — [qué aporta a SU caso en una frase]
   / [experiencia: "En un proyecto de [contexto] aplicamos [práctica]; resultó [efecto]. Les recomendamos [acción]."]

4) Pregunta de cierre (opcional): [una pregunta que obligue a precisar algo].
```

## 3. Lista de verificación de coherencia (úsela con cada grupo)

- [ ] ¿El problema trae un **indicador numérico** (no solo "es lento", "hay errores")?
- [ ] ¿La pregunta se responde con algo más que **sí/no**? ¿Evita el dilema ("¿A o B?") y el futuro ("¿qué pasará…?")?
- [ ] ¿Cada hipótesis dice cómo cambia la **VD** al variar la **VI**, con **dirección** y, si es posible, **umbral**?
- [ ] ¿La VI es **manipulable o al menos medible** antes/después? ¿La VD ya se registra hoy?
- [ ] ¿Existe una **línea base**? Sin "antes" no hay comparación.
- [ ] ¿La evidencia **puede refutar** la hipótesis (criterio de descarte)?
- [ ] ¿El tamaño de muestra/eventos alcanza para lo que afirman? (Eventos raros → solo descriptivo.)
- [ ] ¿Las **4 fuentes** se discuten (qué hicieron/encontraron/aportan) y no solo se listan?
- [ ] Amenazas a la validez: confusión, efecto de observación, un único sitio.

## 4. Banco de aportes cruzados

**Si el grupo es de Arquitectura de Software** (sugerencias de recomendación concreta):
- *Latencia / disponibilidad:* medir **percentiles (p95/p99)** y no promedios; definir un **SLO** y un presupuesto de error antes de
  evaluar la hipótesis; contrastar antes/después con el mismo patrón de carga.
- *Cachés, colas, microservicios:* exigir un **experimento controlado** (flag de funcionalidad, canary) en lugar de comparar
  semanas distintas; registrar tasa de aciertos de caché y consistencia.
- *Deuda técnica y mantenibilidad:* si la VD es "calidad", operacionalizarla (acoplamiento, tiempo de entrega, tasa de fallos
  de cambio).

**Si el grupo es de Inteligencia Artificial:**
- *Evaluación:* separar **entrenamiento/validación/prueba por tiempo** (no al azar) en series temporales; comparar con una
  **línea base simple**; reportar métricas por clase si hay desbalance (precisión/recobrado, no solo exactitud).
- *Operación (MLOps):* definir la métrica de negocio, detección de **deriva** de datos y criterio de reentrenamiento.
- *Datos:* ¿hay etiquetas? ¿quién las produjo? ¿sesgo de selección en los tickets/registros?

**Fuentes adicionales candidatas** (reales; **verificar edición, enlace o DOI antes de citar**, y que se ajusten a su caso):
- Sculley, D., et al. (2015). *Hidden technical debt in machine learning systems.* Advances in Neural Information Processing Systems 28 (NeurIPS).
- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (Eds.). (2016). *Site reliability engineering.* O'Reilly Media. (SLO, presupuesto de error, monitoreo.)
- Kleppmann, M. (2017). *Designing data-intensive applications.* O'Reilly Media. (Confiabilidad, cachés, consistencia.)
- Bass, L., Clements, P., & Kazman, R. (2021). *Software architecture in practice* (4th ed.). Addison-Wesley. (Atributos de calidad y escenarios.)
- Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3rd ed.). OTexts. https://otexts.com/fpp3/ (evaluación de pronósticos con conjunto de prueba).

**Experiencia propia transferible desde este caso** (útil si el grupo trabaja con sensores, alertas o series de tiempo): una alerta
solo sirve si llega **antes** del tiempo de respuesta humano y sin saturar; medir el tiempo de respuesta es parte del diseño, no un extra.
