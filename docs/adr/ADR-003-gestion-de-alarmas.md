# ADR-003 — Gestión de alarmas: una alarma predictiva por llenado

**Estado:** Aceptada · **Contexto:** ISA-18.2 exige que una alarma indique una condición que requiere una respuesta oportuna y
advierte contra la saturación.

**Decisión:** Emitir **un** aviso por llenado cuando el tiempo estimado hasta el 90 % sea igual a la antelación configurada;
no emitir alarmas de nivel intermedias; registrar emisión, acuse y cierre; revisar mensualmente la carga y la tasa de avisos
"decisivos" (los que evitan un rebose).

**Consecuencias:** `+` baja carga (≈ 0,04 avisos por 10 min en la simulación base, semilla 2026), `+` trazabilidad para H2.
`−` ~97 % de los avisos son rutinarios en esa corrida (no evitan un rebose): hay que vigilar la **fatiga** si se amplía el alcance.
`−` la efectividad depende de que el aviso se **perciba**: se recomienda canal redundante.
