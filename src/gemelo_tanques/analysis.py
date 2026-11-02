"""Análisis estadístico de las hipótesis (descriptivo + inferencial, Tema 6; Gillham, 2000)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_confint, proportion_effectsize


def resumen_por_tanque(df: pd.DataFrame) -> pd.DataFrame:
    """Tabla descriptiva: frecuencia, proporción con IC de Wilson, volumen (Tema 6, tabla)."""
    g = df.groupby("tanque").agg(
        llenados=("desborde", "size"), desbordes=("desborde", "sum"),
        margen_medio_min=("margen_reaccion_min", "mean"),
        volumen_desbordado_m3=("volumen_desbordado_m3", "sum"),
    ).reset_index()
    ic = [proportion_confint(r.desbordes, r.llenados, method="wilson") for r in g.itertuples()]
    g["proporcion"] = g["desbordes"] / g["llenados"]
    g["ic95_inf"] = [c[0] for c in ic]
    g["ic95_sup"] = [c[1] for c in ic]
    return g.sort_values("margen_medio_min").reset_index(drop=True)


def comparar_proporciones(x1: int, n1: int, x2: int, n2: int, n_boot: int = 4000,
                          seed: int = 1) -> dict:
    """Grupo 1 (referencia) vs grupo 2 (intervención): Fisher, RR y reducción absoluta con IC bootstrap."""
    p1, p2 = x1 / n1, x2 / n2
    _, p_fisher = stats.fisher_exact([[x1, n1 - x1], [x2, n2 - x2]])
    rng = np.random.default_rng(seed)
    b1 = rng.binomial(n1, p1, n_boot) / n1
    b2 = rng.binomial(n2, p2, n_boot) / n2
    arr = b1 - b2
    with np.errstate(divide="ignore", invalid="ignore"):
        rr = np.where(b1 > 0, b2 / b1, np.nan)
    return {
        "p_referencia": p1, "p_intervencion": p2,
        "reduccion_absoluta": p1 - p2,
        "reduccion_absoluta_ic95": (float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))),
        "riesgo_relativo": (p2 / p1) if p1 > 0 else np.nan,
        "riesgo_relativo_ic95": ((float(np.nanpercentile(rr, 2.5)), float(np.nanpercentile(rr, 97.5)))
                                 if np.isfinite(rr).any() else (np.nan, np.nan)),
        "p_fisher": float(p_fisher),
    }


def mcnemar_pareado(manual: np.ndarray, predictivo: np.ndarray) -> dict:
    """Prueba pareada: mismos llenados bajo ambos modos (solo válido en simulación con CRN)."""
    a = int(((manual == 1) & (predictivo == 1)).sum())
    b = int(((manual == 1) & (predictivo == 0)).sum())
    c = int(((manual == 0) & (predictivo == 1)).sum())
    d = int(((manual == 0) & (predictivo == 0)).sum())
    res = mcnemar([[a, b], [c, d]], exact=True)
    return {"desborda_solo_manual": b, "desborda_solo_predictivo": c, "p_mcnemar": float(res.pvalue)}


def diagnostico_d1(df_manual: pd.DataFrame) -> dict:
    """D1: menor margen de reacción -> mayor probabilidad de desborde (logit a nivel de llenado)."""
    X = sm.add_constant(df_manual[["margen_reaccion_min"]].astype(float))
    m = sm.Logit(df_manual["desborde"].astype(int), X).fit(disp=0)
    or_ = float(np.exp(m.params["margen_reaccion_min"]))
    ic = np.exp(m.conf_int().loc["margen_reaccion_min"].to_numpy())
    # Lectura calculada a partir del OR y su IC (nunca fija)
    if ic[1] < 1:
        lectura = (f"OR = {or_:.2f} con IC95 % por debajo de 1: cada minuto adicional de margen "
                   "reduce las probabilidades de desborde (consistente con D1)")
    elif ic[0] > 1:
        lectura = f"OR = {or_:.2f} con IC95 % por encima de 1: el signo contradice D1"
    else:
        lectura = f"OR = {or_:.2f} con IC95 % que incluye 1: D1 no concluyente con estos datos"
    return {"odds_ratio_por_minuto_de_margen": or_, "ic95": (float(ic[0]), float(ic[1])),
            "p_valor": float(m.pvalues["margen_reaccion_min"]), "lectura": lectura}


def prueba_h2(df_pred: pd.DataFrame, p90_respuesta_min: float) -> dict:
    """H2: avisos con antelación real > P90 del tiempo de respuesta desbordan en menor proporción.

    Se comparan todos los avisos emitidos (acusados o no) según su antelación real.
    Referencia = antelación <= P90; intervención = antelación > P90.
    Criterio de descarte: se descarta si p(> P90) >= p(<= P90).
    """
    d = df_pred[df_pred["modo"] == "predictivo"]
    mayor = d["antelacion_real_min"] > p90_respuesta_min
    lo, hi = d.loc[~mayor, "desborde"], d.loc[mayor, "desborde"]
    if len(lo) == 0 or len(hi) == 0:
        return {"p90_respuesta_min": p90_respuesta_min, "n_menor_igual_p90": len(lo),
                "n_mayor_p90": len(hi), "decision": "NO EVALUABLE (un grupo vacío)"}
    r = comparar_proporciones(int(lo.sum()), len(lo), int(hi.sum()), len(hi))
    descartada = r["p_intervencion"] >= r["p_referencia"]
    return {"p90_respuesta_min": p90_respuesta_min,
            "n_menor_igual_p90": len(lo), "n_mayor_p90": len(hi),
            "p_desborde_menor_igual_p90": r["p_referencia"],
            "p_desborde_mayor_p90": r["p_intervencion"],
            "reduccion_absoluta": r["reduccion_absoluta"],
            "reduccion_absoluta_ic95": r["reduccion_absoluta_ic95"],
            "p_fisher": r["p_fisher"], "H_descartada_por_criterio": bool(descartada),
            "decision": "DESCARTADA" if descartada else
            ("SOSTENIDA (p<0,05)" if r["p_fisher"] < 0.05 else "NO CONCLUYENTE")}


def diagnostico_d2(df_manual: pd.DataFrame) -> dict:
    """D2 con el criterio de descarte del grupo: se descarta si p(otra) <= p(vigilancia)."""
    v = df_manual[df_manual["atencion"] == "vigilancia"]["desborde"]
    o = df_manual[df_manual["atencion"] == "otra_actividad"]["desborde"]
    r = comparar_proporciones(int(v.sum()), len(v), int(o.sum()), len(o))
    descartada = o.mean() <= v.mean()
    return {"p_vigilancia": float(v.mean()), "p_otra_actividad": float(o.mean()),
            "p_fisher": r["p_fisher"], "H_descartada_por_criterio": bool(descartada),
            "decision": "DESCARTADA" if descartada else
            ("SOSTENIDA (p<0,05)" if r["p_fisher"] < 0.05 else "NO CONCLUYENTE")}


def tamano_muestra(p_ref: float, p_obj: float, alfa: float = 0.05, potencia: float = 0.80) -> int:
    """Llenados por grupo (antes/después) para detectar p_ref -> p_obj (Tema 6: tamaño de muestra)."""
    h = proportion_effectsize(p_ref, p_obj)
    n = NormalIndPower().solve_power(effect_size=abs(h), alpha=alfa, power=potencia,
                                     alternative="two-sided")
    return int(np.ceil(n))
