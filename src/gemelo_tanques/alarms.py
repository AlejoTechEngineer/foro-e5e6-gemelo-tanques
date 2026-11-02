"""Indicadores de gestión de alarmas inspirados en ANSI/ISA-18.2-2016.

Referencias orientativas de carga (EEMUA 191, citadas como práctica común y reproducidas en la
literatura de gestión de alarmas; VERIFICAR contra la norma antes de citarlas formalmente):
  <= 1 alarma/10 min por operario  -> carga muy probablemente aceptable
  <= 2 alarmas/10 min              -> manejable
  >= 5 alarmas/10 min              -> sobrecarga
"""
from __future__ import annotations

import numpy as np
import pandas as pd

REFERENCIA_ACEPTABLE_10MIN = 1.0
REFERENCIA_MANEJABLE_10MIN = 2.0


def carga_por_ventana(t_aviso_min: np.ndarray, horizonte_min: float, ventana_min: float = 10.0) -> np.ndarray:
    """Conteo de avisos por ventana fija de `ventana_min` (un operario atiende todos los tanques)."""
    bordes = np.arange(0, horizonte_min + ventana_min, ventana_min)
    cuentas, _ = np.histogram(t_aviso_min, bins=bordes)
    return cuentas


def kpis(df_pred: pd.DataFrame, df_manual: pd.DataFrame, meses: int) -> dict:
    """KPIs de la solución: carga, utilidad (avisos decisivos) y atención oportuna."""
    horizonte = meses * 30 * 24 * 60
    avisos = df_pred.loc[df_pred["modo"] == "predictivo", "t_aviso_min"].dropna().to_numpy()
    cuentas = carga_por_ventana(avisos, horizonte)
    # Aviso "decisivo": el llenado habría desbordado sin aviso (mismo azar) y con aviso no desborda
    decisivo = (df_manual["desborde"].to_numpy() == 1) & (df_pred["desborde"].to_numpy() == 0)
    acusados = df_pred["aviso_acusado"].to_numpy() == 1
    oportunos = acusados & (df_pred["desborde"].to_numpy() == 0)
    return {
        "avisos_por_dia": float(len(avisos) / (meses * 30)),
        "avisos_por_10min_media": float(cuentas.mean()),
        "avisos_por_10min_p99": float(np.percentile(cuentas, 99)),
        "avisos_por_10min_max": int(cuentas.max()),
        "cumple_referencia_aceptable": bool(cuentas.mean() <= REFERENCIA_ACEPTABLE_10MIN),
        "proporcion_avisos_decisivos": float(decisivo.sum() / max(len(avisos), 1)),
        "proporcion_avisos_acusados": float(acusados.mean()),
        "proporcion_acusados_a_tiempo": float(oportunos.sum() / max(acusados.sum(), 1)),
    }
