# Arquitectura propuesta del aviso predictivo (vista de ingeniería)

> Es un diseño de referencia para sustentar la factibilidad de la solución del foro; no hay una implementación productiva
> en este repositorio. El código implementa el **gemelo de simulación** y el **análisis**, no el control de planta.

## 1. Contexto y restricciones

- El **corte automático** de nivel (válvula con enclavamiento) es la salvaguarda primaria y **no** debe depender del software
  de aviso: una alarma es una capa de ayuda al operario, no un sistema instrumentado de seguridad.
- El aviso predictivo es **complementario**: reduce la probabilidad de llegar al alto nivel.
- Restricciones: planta existente (probable PLC/HMI heredados), red industrial segregada de TI, personal no técnico.

## 2. Vista de componentes

```mermaid
flowchart LR
  subgraph Planta["Planta (OT)"]
    S[Sensores de nivel\nultrasónico + alto-alto] --> PLC[PLC / RTU]
    M[Medidores de caudal\ny posición de válvulas] --> PLC
  end
  PLC -- "MQTT / OPC UA" --> GW[Gateway de borde]
  GW --> TS[(Serie de tiempo)]
  GW --> FC[Servicio de pronóstico\nTTT: balance + Holt]
  FC --> AM[Gestor de alarmas\nISA-18.2]
  AD[Detección de anomalías\nresiduo vs. balance] --> AM
  TS --> AD
  AM --> HMI[HMI local\nsirena / luz]
  AM --> MOV[Notificación al operario\nradio / móvil]
  AM --> LOG[(Registro de avisos:\nhora, acuse, respuesta)]
  LOG --> AN[Análisis H1/H2\n(este repositorio)]
```

## 3. Decisiones clave (ver ADRs)

| Decisión | Elección | ADR |
|---|---|---|
| Modelo de pronóstico | Balance de masa como base + Holt; ML profundo se pospone | [ADR-001](adr/ADR-001-pronostico-simple-primero.md) |
| Evaluación previa al piloto | Gemelo de simulación con números aleatorios comunes | [ADR-002](adr/ADR-002-simulacion-crn.md) |
| Alarma | Una sola alarma predictiva por llenado; sin alarmas encadenadas | [ADR-003](adr/ADR-003-gestion-de-alarmas.md) |

## 4. Requisitos no funcionales

| Atributo | Meta | Cómo se verifica |
|---|---|---|
| Latencia extremo a extremo (sensor → aviso) | ≤ 10 s | Marcas de tiempo en el registro de avisos |
| Disponibilidad del servicio de aviso | Degradación elegante: si cae, **el operario sigue con el modo manual** y el enclavamiento protege | Prueba de falla simulada |
| Observabilidad | Cada aviso con id, hora, acuse y cierre | Registro estructurado |
| Seguridad | Segmentación OT/TI; solo-lectura desde el servicio hacia el PLC | Revisión de arquitectura |
| Calidad del dato | Detectar sensor congelado/fuera de rango antes de pronosticar | Pruebas de calidad en el gateway |

## 5. Riesgos

| Riesgo | Efecto | Mitigación |
|---|---|---|
| El aviso no se percibe (operario en otra tarea) | La solución no reduce desbordes (la sensibilidad lo muestra: p(acuse) pesa tanto como la antelación) | Canal redundante (local + móvil); medir acuse |
| Fatiga de alarmas si se extiende a más tanques | Se ignoran los avisos | Mantener carga ≤ 1 aviso / 10 min por operario (referencia a verificar en ISA-18.2) |
| Sensor degradado (incrustación, ruido) | Pronóstico erróneo | Validación de señal; el balance sirve de contraste |
| Efecto Hawthorne en el piloto | Sobrestima el beneficio | Diseño con línea base larga y cambio gradual |
