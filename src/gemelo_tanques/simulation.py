"""Simulación Monte Carlo de llenados con números aleatorios comunes (CRN).

Diseño: primero se generan, por llenado, TODAS las fuentes de azar (caudal real, estado de
atención del operario, retraso de cierre manual, tiempo de respuesta a un aviso, percepción
del aviso y error de pronóstico). Después se aplica el modo de operación ("manual" o
"predictivo"). Así, la comparación manual vs. predictivo es PAREADA: el mismo llenado, el mismo
operario y el mismo azar, y cambia únicamente la intervención.

IMPORTANTE: los datos generados son SINTÉTICOS. Sirven para validar el protocolo de análisis
y el diseño de la solución antes del piloto; no son evidencia empírica del caso.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import Escenario, Lognormal

MIN_POR_MES = 30 * 24 * 60


def _lognormal(rng: np.random.Generator, ln: Lognormal, n: int) -> np.ndarray:
    return rng.lognormal(mean=np.log(ln.mediana_min), sigma=ln.sigma, size=n)


def generar_base(esc: Escenario, meses: int, rng: np.random.Generator,
                 fecha_inicio: str = "2026-03-01") -> pd.DataFrame:
    """Genera los llenados y sus fuentes de azar (sin aplicar aún ningún modo)."""
    op = esc.operario
    tramos = []
    for t in esc.tanques.values():
        n = int(rng.poisson(t.llenados_mes * meses))
        caudal = rng.uniform(t.caudal_min_m3h, t.caudal_max_m3h, n)
        otra = rng.random(n) < op.p_otra_actividad
        d_vig = _lognormal(rng, op.cierre_vigilancia, n)
        d_otra = _lognormal(rng, op.cierre_otra, n)
        tramos.append(pd.DataFrame({
            "tanque": t.nombre,
            "t_inicio_min": rng.uniform(0, meses * MIN_POR_MES, n),
            "caudal_entrada_m3h": caudal,
            "capacidad_m3": t.capacidad_m3,
            "atencion": np.where(otra, "otra_actividad", "vigilancia"),
            "retraso_cierre_manual_min": np.where(otra, d_otra, d_vig),
            "t_respuesta_aviso_min": np.where(otra, _lognormal(rng, op.respuesta_aviso_otra, n),
                                              _lognormal(rng, op.respuesta_aviso_vigilancia, n)),
            "u_acuse": rng.random(n),
            "z_error_pronostico": rng.standard_normal(n),
        }))
    df = pd.concat(tramos, ignore_index=True).sort_values("t_inicio_min").reset_index(drop=True)
    df.insert(0, "llenado_id", np.arange(1, len(df) + 1))
    # Magnitudes derivadas por balance (condición crítica: salida detenida)
    frac = esc.fraccion_margen
    df["margen_reaccion_min"] = frac * df["capacidad_m3"] / df["caudal_entrada_m3h"] * 60
    df["duracion_hasta_objetivo_min"] = (
        (esc.nivel_objetivo - esc.nivel_inicial) * df["capacidad_m3"] / df["caudal_entrada_m3h"] * 60
    )
    inicio = pd.Timestamp(fecha_inicio)
    df["inicio"] = inicio + pd.to_timedelta(df["t_inicio_min"], unit="m")
    df["fecha"] = df["inicio"].dt.date.astype(str)
    df["hora"] = df["inicio"].dt.strftime("%H:%M")
    return df


def aplicar_modo(base: pd.DataFrame, esc: Escenario, modo: str,
                 antelacion_min: float = 6.0, sigma_pronostico_min: float = 0.4,
                 p_acuse_vigilancia: float | None = None,
                 p_acuse_otra: float | None = None) -> pd.DataFrame:
    """Calcula el resultado de cada llenado según el modo de operación.

    modo="manual":     desborda si retraso_cierre_manual > margen_reaccion.
    modo="predictivo": el aviso suena cuando el tiempo estimado hasta el 90 % es `antelacion_min`.
                       Si el operario lo atiende (prob. de acuse), cierra tras `t_respuesta_aviso`
                       desde el aviso; el retraso efectivo tras el objetivo es
                       t_respuesta - antelacion_real. Si no lo atiende, vale el retraso manual.
    """
    if modo not in {"manual", "predictivo"}:
        raise ValueError("modo debe ser 'manual' o 'predictivo'")
    df = base.copy()
    df["modo"] = modo
    margen = df["margen_reaccion_min"].to_numpy()
    d_manual = df["retraso_cierre_manual_min"].to_numpy()

    if modo == "manual":
        retraso = d_manual
        df["antelacion_real_min"] = 0.0
        df["aviso_acusado"] = 0
        df["t_respuesta_min"] = np.nan
    else:
        pv = esc.operario.p_acuse_vigilancia if p_acuse_vigilancia is None else p_acuse_vigilancia
        po = esc.operario.p_acuse_otra if p_acuse_otra is None else p_acuse_otra
        p_acuse = np.where(df["atencion"].to_numpy() == "vigilancia", pv, po)
        acusa = df["u_acuse"].to_numpy() < p_acuse
        # error de pronóstico: aviso emitido con estimación = antelacion; real = antelacion - error
        error = df["z_error_pronostico"].to_numpy() * sigma_pronostico_min
        ant_real = np.clip(antelacion_min - error, 0.0, df["duracion_hasta_objetivo_min"].to_numpy())
        resp = df["t_respuesta_aviso_min"].to_numpy()
        retraso = np.where(acusa, resp - ant_real, d_manual)
        df["antelacion_real_min"] = ant_real
        df["aviso_acusado"] = acusa.astype(int)
        df["t_respuesta_min"] = np.where(acusa, resp, np.nan)

    exceso = np.maximum(retraso - margen, 0.0)
    df["retraso_cierre_efectivo_min"] = retraso
    df["desborde"] = (exceso > 0).astype(int)
    df["duracion_desborde_min"] = exceso
    df["volumen_desbordado_m3"] = exceso / 60.0 * df["caudal_entrada_m3h"]
    # momento (min absolutos del mes) en que sonaría el aviso
    df["t_aviso_min"] = np.where(
        df["modo"] == "predictivo",
        df["t_inicio_min"] + df["duracion_hasta_objetivo_min"] - df["antelacion_real_min"],
        np.nan,
    )
    return df


def registro_comun(df: pd.DataFrame) -> pd.DataFrame:
    """Proyección al esquema del 'registro común' del foro (ver data/plantillas)."""
    cols = ["llenado_id", "fecha", "hora", "tanque", "atencion", "caudal_entrada_m3h",
            "margen_reaccion_min", "modo", "aviso_acusado", "t_respuesta_min",
            "desborde", "duracion_desborde_min", "volumen_desbordado_m3"]
    out = df[cols].copy()
    for c in ("margen_reaccion_min", "duracion_desborde_min", "volumen_desbordado_m3",
              "caudal_entrada_m3h", "t_respuesta_min"):
        out[c] = out[c].round(3)
    return out


def tasa_mensual_esperada(esc: Escenario, meses: int = 240, seed: int = 0) -> pd.DataFrame:
    """Desbordes esperados por mes y tanque en modo manual (para validar la calibración)."""
    rng = np.random.default_rng(seed)
    d = aplicar_modo(generar_base(esc, meses, rng), esc, "manual")
    g = d.groupby("tanque").agg(llenados=("desborde", "size"), desbordes=("desborde", "sum"))
    g["desbordes_por_mes"] = g["desbordes"] / meses
    g["proporcion_desborde"] = g["desbordes"] / g["llenados"]
    g["observado_min"] = [esc.observado_mes[t][0] for t in g.index]
    g["observado_max"] = [esc.observado_mes[t][1] for t in g.index]
    g["dentro_de_rango"] = (g["desbordes_por_mes"] >= g["observado_min"] * 0.7) & \
                           (g["desbordes_por_mes"] <= g["observado_max"] * 1.3)
    return g.reset_index()
