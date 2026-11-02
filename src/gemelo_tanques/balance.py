"""Balance de masa y margen de reacción (variable independiente de la H1 diagnóstica).

Definición del grupo: margen de reacción = tiempo que tarda un tanque en llenar su
último 10 % con la transferencia de salida detenida (condición crítica).
Con la salida detenida el consumo se toma como 0, que es el peor caso.
"""
from __future__ import annotations

import math

from .config import Tanque


def margen_reaccion_min(capacidad_m3: float, caudal_entrada_m3h: float,
                        consumo_m3h: float = 0.0, fraccion_final: float = 0.10) -> float:
    """Minutos para llenar `fraccion_final` de la capacidad con el caudal neto dado."""
    neto = caudal_entrada_m3h - consumo_m3h
    if neto <= 0:
        return math.inf
    return fraccion_final * capacidad_m3 / neto * 60.0


def duracion_llenado_min(capacidad_m3: float, caudal_m3h: float,
                         nivel_ini: float, nivel_fin: float) -> float:
    """Minutos para pasar de `nivel_ini` a `nivel_fin` (fracciones de la capacidad)."""
    return (nivel_fin - nivel_ini) * capacidad_m3 / caudal_m3h * 60.0


def tabla_margenes(tanques: dict[str, Tanque], fraccion: float = 0.10) -> list[dict]:
    """Margen conservador (caudal máximo), nominal y optimista (caudal mínimo) por tanque."""
    filas = []
    for t in tanques.values():
        filas.append({
            "tanque": t.nombre,
            "capacidad_m3_supuesta": t.capacidad_m3,
            "caudal_min_m3h": t.caudal_min_m3h,
            "caudal_max_m3h": t.caudal_max_m3h,
            "margen_min_conservador": margen_reaccion_min(t.capacidad_m3, t.caudal_max_m3h, 0, fraccion),
            "margen_min_nominal": margen_reaccion_min(t.capacidad_m3, t.caudal_nominal_m3h, 0, fraccion),
            "margen_min_optimista": margen_reaccion_min(t.capacidad_m3, t.caudal_min_m3h, 0, fraccion),
        })
    return sorted(filas, key=lambda f: f["margen_min_conservador"])
