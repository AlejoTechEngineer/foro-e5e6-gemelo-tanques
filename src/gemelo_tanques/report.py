"""Figuras del análisis (matplotlib, sin estilos externos)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

COLORES = {"manual": "#b45309", "predictivo": "#0f766e", "ref": "#475569"}


def _guardar(fig, ruta: Path) -> str:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    return str(ruta)


def fig_margenes(tabla: list[dict], ruta: Path) -> str:
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    nombres = [f["tanque"] for f in tabla]
    x = np.arange(len(nombres))
    ax.bar(x - 0.2, [f["margen_min_conservador"] for f in tabla], 0.4, label="Conservador (Q máx.)",
           color=COLORES["manual"])
    ax.bar(x + 0.2, [f["margen_min_optimista"] for f in tabla], 0.4, label="Optimista (Q mín.)",
           color=COLORES["ref"])
    ax.set_xticks(x, nombres)
    ax.set_ylabel("Margen de reacción (min)")
    ax.set_title("Margen de reacción por tanque (salida detenida; capacidades supuestas)")
    ax.legend()
    return _guardar(fig, ruta)


def fig_calibracion(cal: pd.DataFrame, ruta: Path) -> str:
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    x = np.arange(len(cal))
    for i, r in enumerate(cal.itertuples()):
        ax.plot([i, i], [r.observado_min, r.observado_max], lw=8, color=COLORES["ref"], alpha=.35,
                solid_capstyle="butt", label="Rango observado (caso)" if i == 0 else None)
    ax.scatter(x, cal["desbordes_por_mes"], color=COLORES["manual"], zorder=3,
               label="Simulado (240 meses)")
    ax.set_xticks(x, cal["tanque"])
    ax.set_ylabel("Desbordes por mes")
    ax.set_title("Calibración del modo manual vs. frecuencias del caso")
    ax.legend()
    return _guardar(fig, ruta)


def fig_pronostico(resumen: pd.DataFrame, ruta: Path) -> str:
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    p = resumen.pivot(index="horizonte_min", columns="metodo", values="rmse_min").sort_index(ascending=False)
    p.plot(kind="bar", ax=ax, rot=0, color=[COLORES["ref"], "#0f766e", "#7c3aed"][: p.shape[1]])
    ax.set_xlabel("Horizonte: minutos reales que faltan para el 90 %")
    ax.set_ylabel("RMSE del tiempo estimado (min)")
    ax.set_title("Pronóstico de tiempo a objetivo en el conjunto de prueba")
    ax.legend(title="Método")
    return _guardar(fig, ruta)


def fig_intervencion(res_manual: pd.DataFrame, res_pred: pd.DataFrame, ruta: Path) -> str:
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    orden = list(res_manual["tanque"])
    x = np.arange(len(orden))
    for k, (df, lab, off) in enumerate(((res_manual, "manual", -0.2), (res_pred, "predictivo", 0.2))):
        d = df.set_index("tanque").loc[orden]
        ax.bar(x + off, d["proporcion"] * 100, 0.4, label=lab, color=COLORES[lab],
               yerr=[np.clip((d["proporcion"] - d["ic95_inf"]) * 100, 0, None),
                     np.clip((d["ic95_sup"] - d["proporcion"]) * 100, 0, None)],
               capsize=3)
    ax.set_xticks(x, orden)
    ax.set_ylabel("Llenados con desborde (%)")
    ax.set_title("Proporción de desborde por tanque (6 meses simulados, IC 95 % Wilson)")
    ax.legend()
    return _guardar(fig, ruta)


def fig_sensibilidad(sens: pd.DataFrame, p90_otra: float, base_manual: float, ruta: Path) -> str:
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
    for p, g in sens.groupby("p_acuse_otra"):
        axs[0].plot(g["antelacion_min"], g["proporcion_desborde"] * 100, marker="o", ms=3,
                    label=f"p(acuse | otra act.) = {p:.2f}")
    axs[0].axhline(base_manual * 100, ls="--", color=COLORES["manual"], label="Manual (línea base)")
    axs[0].set_xlabel("Antelación del aviso (min)")
    axs[0].set_ylabel("Llenados con desborde (%)")
    axs[0].set_title("Eficacia según antelación y atención del aviso")
    axs[0].legend(fontsize=7)
    g = sens[sens["p_acuse_otra"] == sens["p_acuse_otra"].max()]
    axs[1].plot(g["antelacion_min"], g["pct_a_tiempo_acusados"] * 100, marker="o", color=COLORES["predictivo"])
    axs[1].axvline(p90_otra, ls=":", color=COLORES["ref"])
    axs[1].text(p90_otra + .1, 96.2, "P90 respuesta\n(otra actividad)", fontsize=7)
    axs[1].set_xlabel("Antelación del aviso (min)")
    axs[1].set_ylabel("Avisos atendidos a tiempo (%)")
    axs[1].set_title("H2: respuesta oportuna vs. antelación")
    return _guardar(fig, ruta)
