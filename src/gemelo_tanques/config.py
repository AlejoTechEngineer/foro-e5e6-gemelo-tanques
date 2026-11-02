"""Carga y validación de la configuración del escenario."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Tanque:
    nombre: str
    capacidad_m3: float
    caudal_min_m3h: float
    caudal_max_m3h: float
    llenados_mes: float

    @property
    def caudal_nominal_m3h(self) -> float:
        return (self.caudal_min_m3h + self.caudal_max_m3h) / 2


@dataclass(frozen=True)
class Lognormal:
    mediana_min: float
    sigma: float


@dataclass(frozen=True)
class Operario:
    p_otra_actividad: float
    cierre_vigilancia: Lognormal
    cierre_otra: Lognormal
    respuesta_aviso_vigilancia: Lognormal
    respuesta_aviso_otra: Lognormal
    p_acuse_vigilancia: float
    p_acuse_otra: float


@dataclass(frozen=True)
class Escenario:
    nivel_objetivo: float
    nivel_inicial: float
    fraccion_margen: float
    ruido_sensor_pct: float
    deriva_caudal_pct: float
    tanques: dict[str, Tanque]
    operario: Operario
    observado_mes: dict[str, tuple[float, float]]


def _ln(d: dict) -> Lognormal:
    return Lognormal(float(d["mediana_min"]), float(d["sigma"]))


def cargar(ruta: str | Path) -> Escenario:
    raw = yaml.safe_load(Path(ruta).read_text(encoding="utf-8"))
    tanques = {
        k: Tanque(k, float(v["capacidad_m3"]), float(v["caudal_min_m3h"]),
                  float(v["caudal_max_m3h"]), float(v["llenados_mes"]))
        for k, v in raw["tanques"].items()
    }
    for t in tanques.values():
        if t.caudal_min_m3h <= 0 or t.caudal_max_m3h < t.caudal_min_m3h or t.capacidad_m3 <= 0:
            raise ValueError(f"Parámetros inválidos en tanque {t.nombre}")
    o = raw["operario"]
    operario = Operario(
        float(o["p_otra_actividad"]), _ln(o["cierre_vigilancia"]), _ln(o["cierre_otra"]),
        _ln(o["respuesta_aviso_vigilancia"]), _ln(o["respuesta_aviso_otra"]), float(o["p_acuse_vigilancia"]), float(o["p_acuse_otra"]),
    )
    if not (0 < raw["nivel_inicial"] < raw["nivel_objetivo"] < 1):
        raise ValueError("Se requiere 0 < nivel_inicial < nivel_objetivo < 1")
    return Escenario(
        float(raw["nivel_objetivo"]), float(raw["nivel_inicial"]), float(raw["fraccion_margen"]),
        float(raw["ruido_sensor_pct"]), float(raw["deriva_caudal_pct"]), tanques, operario,
        {k: (float(v[0]), float(v[1])) for k, v in raw["observado_mes"].items()},
    )
