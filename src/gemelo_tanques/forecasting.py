"""Pronóstico del tiempo hasta el nivel objetivo (TTT) y evaluación con partición temporal.

Siguiendo Hyndman & Athanasopoulos (2021): (1) el pronóstico se evalúa con datos NO usados para
ajustarlo (primera mitad de los llenados = ajuste de hiperparámetros; segunda = prueba) y
(2) se compara contra una referencia simple (el balance de masa nominal).

Métodos:
  balance : referencia. TTT = (objetivo - nivel) / (caudal_nominal / capacidad). No usa datos del llenado.
  ols     : regresión lineal móvil sobre los últimos `ventana_min` minutos de lecturas del sensor.
  holt    : suavizado exponencial doble (nivel + tendencia) sobre las lecturas.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import Escenario, Tanque

DT_S = 10.0  # periodo de muestreo del sensor (s)


@dataclass
class Traza:
    t_min: np.ndarray       # tiempo desde el inicio del llenado (min)
    nivel_real: np.ndarray  # fracción de capacidad (sin ruido)
    nivel_med: np.ndarray   # lectura del sensor (con ruido)
    t_objetivo_min: float   # instante real en que se alcanza el objetivo


def trazar_nivel(tanque: Tanque, esc: Escenario, caudal_m3h: float,
                 rng: np.random.Generator) -> Traza:
    """Genera la serie de nivel de un llenado con deriva lenta de caudal y ruido de sensor."""
    dt_min = DT_S / 60.0
    t_obj = (esc.nivel_objetivo - esc.nivel_inicial) * tanque.capacidad_m3 / caudal_m3h * 60
    n = int(np.ceil((t_obj + 2.0) / dt_min)) + 1
    t = np.arange(n) * dt_min
    # deriva AR(1) del caudal (presión de red)
    eps = rng.standard_normal(n) * (esc.deriva_caudal_pct / 100) * 0.15
    deriva = np.zeros(n)
    for i in range(1, n):
        deriva[i] = 0.98 * deriva[i - 1] + eps[i]
    q = caudal_m3h * (1 + deriva)
    nivel = esc.nivel_inicial + np.cumsum(q / tanque.capacidad_m3 / 60.0 * dt_min) - q[0] / tanque.capacidad_m3 / 60 * dt_min
    medido = nivel + rng.standard_normal(n) * (esc.ruido_sensor_pct / 100)
    # el instante real de objetivo sale de la serie (incluye la deriva)
    idx = int(np.searchsorted(nivel, esc.nivel_objetivo))
    t_real = float(t[min(idx, n - 1)])
    return Traza(t, nivel, medido, t_real)


def ttt_balance(nivel_actual: float, tanque: Tanque, objetivo: float) -> float:
    rate_min = tanque.caudal_nominal_m3h / tanque.capacidad_m3 / 60.0
    return max((objetivo - nivel_actual) / rate_min, 0.0)


def ttt_ols(t: np.ndarray, y: np.ndarray, i: int, objetivo: float, ventana_min: float) -> float:
    dt_min = DT_S / 60.0
    k = max(round(ventana_min / dt_min), 3)
    lo = max(0, i - k + 1)
    tt, yy = t[lo:i + 1], y[lo:i + 1]
    if len(tt) < 3:
        return np.nan
    pend, ord_ = np.polyfit(tt, yy, 1)
    if pend <= 1e-9:
        return np.nan
    nivel_ajustado = pend * t[i] + ord_
    return max((objetivo - nivel_ajustado) / pend, 0.0)


def ttt_holt(y: np.ndarray, t: np.ndarray, i: int, objetivo: float,
             alpha: float, beta: float) -> float:
    nivel, tend = y[0], 0.0
    dt_min = DT_S / 60.0
    for j in range(1, i + 1):
        previo = nivel
        nivel = alpha * y[j] + (1 - alpha) * (nivel + tend)
        tend = beta * (nivel - previo) + (1 - beta) * tend
    pend = tend / dt_min
    if pend <= 1e-9:
        return np.nan
    return max((objetivo - nivel) / pend, 0.0)


def _estimaciones(traza: Traza, tanque: Tanque, esc: Escenario, horizonte_min: float,
                  p: dict) -> dict[str, float] | None:
    """Estimaciones de TTT en el instante en que el TTT real es `horizonte_min`."""
    t_eval = traza.t_objetivo_min - horizonte_min
    if t_eval < 3.0:
        return None
    i = int(np.searchsorted(traza.t_min, t_eval))
    y = traza.nivel_med
    return {
        "balance": ttt_balance(y[i], tanque, esc.nivel_objetivo),
        "ols": ttt_ols(traza.t_min, y, i, esc.nivel_objetivo, p["ventana_min"]),
        "holt": ttt_holt(y, traza.t_min, i, esc.nivel_objetivo, p["alpha"], p["beta"]),
        "_real": traza.t_objetivo_min - traza.t_min[i],
    }


def evaluar(esc: Escenario, n_por_tanque: int = 60, horizontes=(10.0, 5.0, 3.0),
            seed: int = 7) -> tuple[pd.DataFrame, dict]:
    """Ajusta hiperparámetros con la 1.ª mitad y reporta el error en la 2.ª (prueba)."""
    rng = np.random.default_rng(seed)
    trazas = []
    for t in esc.tanques.values():
        for _ in range(n_por_tanque):
            q = rng.uniform(t.caudal_min_m3h, t.caudal_max_m3h)
            trazas.append((t, trazar_nivel(t, esc, q, rng)))
    orden = rng.permutation(len(trazas))
    corte = len(trazas) // 2
    train = [trazas[i] for i in orden[:corte]]
    test = [trazas[i] for i in orden[corte:]]

    def rmse_conj(conjunto, params, metodo, h=5.0):
        e = []
        for tq, tr in conjunto:
            r = _estimaciones(tr, tq, esc, h, params)
            if r and not np.isnan(r[metodo]):
                e.append(r[metodo] - r["_real"])
        return np.sqrt(np.mean(np.square(e))) if e else np.inf

    mejor_ols = min(({"ventana_min": v, "alpha": .3, "beta": .1} for v in (1, 2, 3, 5)),
                    key=lambda p: rmse_conj(train, p, "ols"))
    mejor_holt = min(({"ventana_min": 2, "alpha": a, "beta": b}
                      for a in (.1, .2, .3, .5) for b in (.02, .05, .1, .2)),
                     key=lambda p: rmse_conj(train, p, "holt"))
    params = {"ventana_min": mejor_ols["ventana_min"], "alpha": mejor_holt["alpha"],
              "beta": mejor_holt["beta"]}

    filas = []
    for tq, tr in test:
        for h in horizontes:
            r = _estimaciones(tr, tq, esc, h, params)
            if not r:
                continue
            for m in ("balance", "ols", "holt"):
                if not np.isnan(r[m]):
                    filas.append({"tanque": tq.nombre, "horizonte_min": h, "metodo": m,
                                  "error_min": r[m] - r["_real"]})
    err = pd.DataFrame(filas)
    resumen = (err.assign(abs_error=err["error_min"].abs(), sq=err["error_min"] ** 2)
                  .groupby(["horizonte_min", "metodo"])
                  .agg(n=("error_min", "size"), sesgo_min=("error_min", "mean"),
                       mae_min=("abs_error", "mean"), rmse_min=("sq", lambda s: np.sqrt(s.mean())))
                  .reset_index())
    return resumen, params
