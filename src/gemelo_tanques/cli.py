"""Línea de comandos: reproduce todos los resultados del repositorio."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import alarms, analysis, balance, config, forecasting, report, simulation

ANTELACION_BASE_MIN = 6.0


def _md(df: pd.DataFrame, nd: int = 3) -> str:
    return df.round(nd).to_markdown(index=False)


def ejecutar_todo(ruta_cfg: Path, salida: Path, datos: Path, seed: int, meses: int = 6) -> dict:
    esc = config.cargar(ruta_cfg)
    figs = salida / "figures"
    figs.mkdir(parents=True, exist_ok=True)
    R: dict = {"seed": seed, "meses": meses}

    # 1. Margen de reacción por balance (H1 diagnóstica)
    tabla = balance.tabla_margenes(esc.tanques, esc.fraccion_margen)
    pd.DataFrame(tabla).to_csv(salida / "margenes_reaccion.csv", index=False)
    report.fig_margenes(tabla, figs / "fig1_margenes.png")

    # 2. Calibración del modo manual contra el caso
    cal = simulation.tasa_mensual_esperada(esc, meses=240, seed=seed)
    cal.to_csv(salida / "calibracion.csv", index=False)
    report.fig_calibracion(cal, figs / "fig2_calibracion.png")

    # 3. Pronóstico del tiempo a objetivo (partición temporal, referencia simple)
    pron, params = forecasting.evaluar(esc, seed=seed)
    pron.to_csv(salida / "pronostico.csv", index=False)
    report.fig_pronostico(pron, figs / "fig3_pronostico.png")
    mejor5 = pron[pron["horizonte_min"] == 5.0].sort_values("rmse_min").iloc[0]
    sigma_pron = float(np.ceil(mejor5["rmse_min"] * 10) / 10)  # RMSE a 5 min, redondeado hacia arriba

    # 4. Datos sintéticos (6 meses) + línea base manual: D1 y D2 (diagnóstico)
    rng = np.random.default_rng(seed)
    base = simulation.generar_base(esc, meses, rng)
    man = simulation.aplicar_modo(base, esc, "manual")
    pre = simulation.aplicar_modo(base, esc, "predictivo", ANTELACION_BASE_MIN, sigma_pron)
    datos.mkdir(parents=True, exist_ok=True)
    simulation.registro_comun(man).to_csv(datos / "registro_llenados_manual.csv", index=False)
    simulation.registro_comun(pre).to_csv(datos / "registro_llenados_predictivo_paired.csv", index=False)
    R["d1"] = analysis.diagnostico_d1(man)
    R["d2"] = analysis.diagnostico_d2(man)
    res_man = analysis.resumen_por_tanque(man)
    res_man.to_csv(salida / "resumen_manual_por_tanque.csv", index=False)

    # 5. H1 (solución): diseño antes/después NO pareado (como será el piloto real)
    base_b = simulation.generar_base(esc, meses, np.random.default_rng(seed + 1))
    pre_b = simulation.aplicar_modo(base_b, esc, "predictivo", ANTELACION_BASE_MIN, sigma_pron)
    res_pre = analysis.resumen_por_tanque(pre_b)
    res_pre.to_csv(salida / "resumen_predictivo_por_tanque.csv", index=False)
    R["h1_global"] = analysis.comparar_proporciones(
        int(man["desborde"].sum()), len(man), int(pre_b["desborde"].sum()), len(pre_b))
    R["h1_por_tanque"] = {}
    for t in esc.tanques:
        a, b = man[man.tanque == t], pre_b[pre_b.tanque == t]
        R["h1_por_tanque"][t] = analysis.comparar_proporciones(
            int(a["desborde"].sum()), len(a), int(b["desborde"].sum()), len(b))
    R["h1_pareado"] = analysis.mcnemar_pareado(man["desborde"].to_numpy(), pre["desborde"].to_numpy())
    R["alarmas"] = alarms.kpis(pre, man, meses)
    report.fig_intervencion(res_man, res_pre, figs / "fig4_intervencion.png")

    # 6. Sensibilidad (H2): antelación x probabilidad de acuse, con 240 meses para estabilidad
    base_s = simulation.generar_base(esc, 240, np.random.default_rng(seed + 2))
    man_s = simulation.aplicar_modo(base_s, esc, "manual")
    filas = []
    corridas_h2 = []  # avisos con el acuse del YAML, para la prueba directa de H2
    for p_otra in (0.50, 0.70, 0.85, 1.00):
        for L in (0, 1, 2, 3, 4, 6, 8, 10, 12):
            d = simulation.aplicar_modo(base_s, esc, "predictivo", float(L), sigma_pron,
                                        p_acuse_otra=p_otra)
            ac = d[d["aviso_acusado"] == 1]
            filas.append({"p_acuse_otra": p_otra, "antelacion_min": L,
                          "proporcion_desborde": d["desborde"].mean(),
                          "pct_a_tiempo_acusados": 1 - ac["desborde"].mean()})
            if p_otra == esc.operario.p_acuse_otra:
                corridas_h2.append(d[["modo", "antelacion_real_min", "desborde"]])
    sens = pd.DataFrame(filas)
    sens.to_csv(salida / "sensibilidad.csv", index=False)
    p90_otra = float(base_s.loc[base_s.atencion == "otra_actividad", "t_respuesta_aviso_min"].quantile(.9))
    R["p90_respuesta_otra_min"] = p90_otra
    # Prueba directa de H2: antelación real > P90 vs. <= P90 (todas las antelaciones de la malla)
    R["h2"] = analysis.prueba_h2(pd.concat(corridas_h2, ignore_index=True), p90_otra)
    R["base_manual_proporcion"] = float(man_s["desborde"].mean())
    report.fig_sensibilidad(sens, p90_otra, float(man_s["desborde"].mean()), figs / "fig5_sensibilidad.png")

    # 7. Tamaño de muestra del piloto (Tema 6)
    p0 = float(man_s["desborde"].mean())
    R["muestra"] = {
        "p_base": p0,
        "n_por_grupo_reduccion_75pct": analysis.tamano_muestra(p0, p0 * 0.25),
        "n_por_grupo_reduccion_50pct": analysis.tamano_muestra(p0, p0 * 0.50),
        "llenados_totales_mes": float(sum(t.llenados_mes for t in esc.tanques.values())),
    }

    # 8. Resumen en Markdown
    (salida / "resumen_resultados.md").write_text(_resumen_md(R, esc, tabla, cal, pron, params,
                                                              res_man, res_pre, sens), encoding="utf-8")
    (salida / "resultados.json").write_text(json.dumps(R, indent=2, default=float, ensure_ascii=False),
                                            encoding="utf-8")
    return R



def _lectura_pronostico(pron: pd.DataFrame) -> str:
    """Frase calculada: qué método gana en cada horizonte frente a la referencia simple."""
    partes = []
    for h, g in pron.groupby("horizonte_min"):
        ref = float(g.loc[g.metodo == "balance", "rmse_min"].iloc[0])
        mejor = g.sort_values("rmse_min").iloc[0]
        if mejor["metodo"] == "balance":
            partes.append(f"a {h:.0f} min ningún método supera al balance (RMSE {ref:.2f})")
        else:
            partes.append(f"a {h:.0f} min gana {mejor['metodo']} (RMSE {mejor['rmse_min']:.2f} vs. {ref:.2f} del balance)")
    perdedores = pron[(pron.metodo != "balance")].merge(
        pron[pron.metodo == "balance"][["horizonte_min", "rmse_min"]], on="horizonte_min", suffixes=("", "_ref"))
    peores = perdedores[perdedores.rmse_min > perdedores.rmse_min_ref]
    extra = ""
    if len(peores):
        extra = " Empeoran la referencia: " + ", ".join(
            f"{r.metodo} a {r.horizonte_min:.0f} min" for r in peores.itertuples()) + "."
    return ("Lectura (calculada): " + "; ".join(partes) + "." + extra +
            " Se reporta tal cual: Hyndman & Athanasopoulos (2021) exigen comparar contra referencias simples.")


def _lectura_antelacion(piv: pd.DataFrame, base_manual: float, p90: float) -> str:
    """Frase calculada: desde qué antelación el aviso supera a la operación manual."""
    mejora = piv[piv.proporcion_desborde < base_manual]
    peor = piv[piv.proporcion_desborde >= base_manual]
    l_mejora = mejora.antelacion_min.min() if len(mejora) else None
    l99 = piv[piv.pct_a_tiempo_acusados >= 0.99].antelacion_min.min() if (piv.pct_a_tiempo_acusados >= 0.99).any() else None
    txt = "Lectura (calculada): "
    if len(peor):
        txt += (f"con antelación ≤ {peor.antelacion_min.max():.0f} min el aviso NO mejora la operación manual; ")
    if l_mejora is not None:
        txt += f"la supera desde {l_mejora:.0f} min; "
    if l99 is not None:
        txt += f"≥ 99 % de los avisos acusados se atienden a tiempo desde {l99:.0f} min (P90 de respuesta ≈ {p90:.1f} min). "
    return txt + "Es consecuencia del modelo y sus supuestos, no un hallazgo del caso."


def _resumen_md(R, esc, tabla, cal, pron, params, res_man, res_pre, sens) -> str:
    h1 = R["h1_global"]
    s = []
    s.append("# Resultados de la simulación (DATOS SINTÉTICOS)\n")
    s.append("> **Advertencia de integridad.** Estos resultados provienen de un modelo con supuestos "
             "(capacidades, llenados/mes, comportamiento del operario) calibrado únicamente con los rangos "
             "de desbordes del caso. **No son evidencia empírica** ni deben citarse como hallazgos. "
             "Validan el *protocolo de análisis* y el *diseño de la solución* antes del piloto.\n")
    s.append(f"Semilla: `{R['seed']}` · Horizonte: {R['meses']} meses · Antelación base del aviso: "
             f"{ANTELACION_BASE_MIN:.0f} min\n")
    s.append("## 1. Margen de reacción por balance (variable de la H1 diagnóstica)\n")
    s.append(_md(pd.DataFrame(tabla), 2) + "\n")
    s.append("## 2. Calibración del modo manual (240 meses simulados vs. rangos del caso)\n")
    s.append(_md(cal[["tanque", "llenados", "desbordes_por_mes", "proporcion_desborde",
                      "observado_min", "observado_max", "dentro_de_rango"]], 4) + "\n")
    s.append("## 3. Diagnóstico con la línea base manual (6 meses)\n")
    s.append(_md(res_man, 3) + "\n")
    d1, d2 = R["d1"], R["d2"]
    s.append(f"- **D1 (margen → desborde):** OR por minuto de margen = {d1['odds_ratio_por_minuto_de_margen']:.2f} "
             f"(IC95 % {d1['ic95'][0]:.2f}–{d1['ic95'][1]:.2f}; p = {d1['p_valor']:.3g}). "
             f"Lectura (calculada): {d1['lectura']}. *Limitación:* el margen varía sobre todo **entre** tanques, de modo que D1 está confundida con "
             "características propias de cada tanque (ver `docs/03`, validez interna).")
    s.append(f"- **D2 (atención → desborde):** p(vigilancia) = {d2['p_vigilancia']:.3f}; "
             f"p(otra actividad) = {d2['p_otra_actividad']:.3f}; Fisher p = {d2['p_fisher']:.2g}. "
             f"Decisión con el criterio de descarte del grupo: **{d2['decision']}**.\n")
    s.append("## 4. Pronóstico del tiempo hasta el 90 % (conjunto de prueba)\n")
    s.append(f"Hiperparámetros ajustados solo con la primera mitad: {params}.\n")
    s.append(_md(pron, 3) + "\n")
    s.append(_lectura_pronostico(pron) + "\n")
    s.append("## 5. H1 (solución): aviso predictivo vs. manual — diseño antes/después no pareado\n")
    s.append(_md(res_pre, 3) + "\n")
    rrci = h1["riesgo_relativo_ic95"]; arci = h1["reduccion_absoluta_ic95"]
    s.append(f"- Global: {h1['p_referencia']*100:.2f} % → {h1['p_intervencion']*100:.2f} % "
             f"(reducción absoluta {h1['reduccion_absoluta']*100:.2f} pp; IC95 % bootstrap "
             f"{arci[0]*100:.2f}–{arci[1]*100:.2f}; RR = {h1['riesgo_relativo']:.2f}, "
             f"IC95 % {rrci[0]:.2f}–{rrci[1]:.2f}; Fisher p = {h1['p_fisher']:.2g}).")
    for t, r in R["h1_por_tanque"].items():
        s.append(f"  - {t}: {r['p_referencia']*100:.2f} % → {r['p_intervencion']*100:.2f} % "
                 f"(reducción absoluta {r['reduccion_absoluta']*100:.2f} pp)")
    s.append(_lectura_h1_margen(R["h1_por_tanque"], res_man))
    mc = R["h1_pareado"]
    s.append(f"- Comparación pareada (mismo azar): desbordan solo en manual = {mc['desborda_solo_manual']}, "
             f"solo en predictivo = {mc['desborda_solo_predictivo']}; McNemar exacto p = {mc['p_mcnemar']:.2g}. "
             "*Solo posible en simulación; el piloto real será no pareado.*\n")
    a = R["alarmas"]
    s.append("## 6. Carga de alarmas (inspirada en ISA-18.2)\n")
    s.append(f"- Avisos/día: {a['avisos_por_dia']:.1f}; por 10 min: media {a['avisos_por_10min_media']:.3f}, "
             f"p99 {a['avisos_por_10min_p99']:.0f}, máx. {a['avisos_por_10min_max']}. "
             f"¿Bajo la referencia de 1/10 min? **{'Sí' if a['cumple_referencia_aceptable'] else 'No'}**.")
    s.append(f"- Avisos decisivos (habrían desbordado sin aviso): {a['proporcion_avisos_decisivos']*100:.1f} %. "
             + ("El resto son avisos rutinarios; la carga media queda bajo la referencia, pero cabe vigilar "
                "la fatiga si se añaden más tanques.\n" if a["cumple_referencia_aceptable"] else
                "El resto son avisos rutinarios y la carga media SUPERA la referencia: riesgo de fatiga "
                "de alarmas; revisar umbrales antes del piloto.\n"))
    s.append("## 7. H2: antelación del aviso\n")
    s.append(f"P90 del tiempo de respuesta cuando el operario está en otra actividad ≈ {R['p90_respuesta_otra_min']:.1f} min. "
             f"Línea base manual: {R['base_manual_proporcion']*100:.2f} % de llenados con desborde.\n")
    piv = sens[sens.p_acuse_otra == 0.85].round(4)
    s.append(_md(piv, 4) + "\n")
    s.append(_lectura_antelacion(piv, R["base_manual_proporcion"], R["p90_respuesta_otra_min"]) + "\n")
    h2 = R["h2"]
    if "p_fisher" in h2:
        s.append(f"**Prueba directa de H2** (avisos de todas las antelaciones de la malla, acuse del YAML): "
                 f"antelación real ≤ P90 ({h2['p90_respuesta_min']:.1f} min): "
                 f"{h2['p_desborde_menor_igual_p90']*100:.2f} % con desborde (n = {h2['n_menor_igual_p90']}); "
                 f"> P90: {h2['p_desborde_mayor_p90']*100:.2f} % (n = {h2['n_mayor_p90']}); "
                 f"Fisher p {'< 0,001' if h2['p_fisher'] < 0.001 else '= ' + format(h2['p_fisher'], '.2g')}. Decisión con el criterio de descarte: **{h2['decision']}**. "
                 "*La proporción de cada grupo depende de qué antelaciones se incluyan en la malla.*\n")
    else:
        s.append(f"**Prueba directa de H2:** {h2['decision']}.\n")
    m = R["muestra"]
    meses_fase = m["n_por_grupo_reduccion_75pct"] / m["llenados_totales_mes"]
    s.append("## 8. Tamaño de muestra del piloto\n")
    s.append(f"Con p base ≈ {m['p_base']*100:.2f} %, detectar una reducción del 75 % requiere ≈ "
             f"{m['n_por_grupo_reduccion_75pct']} llenados por grupo y del 50 %, ≈ {m['n_por_grupo_reduccion_50pct']} "
             f"(α = 0,05; potencia 0,80). Con ≈ {m['llenados_totales_mes']:.0f} llenados/mes (supuesto), "
             f"la reducción del 75 % exige ≈ {meses_fase:.1f} meses por fase.\n")
    return "\n".join(s)


def _lectura_h1_margen(por_tanque: dict, res_man: pd.DataFrame) -> str:
    """Frase calculada: ¿la reducción absoluta es mayor en los tanques de menor margen? (H1)."""
    margen = res_man.set_index("tanque")["margen_medio_min"]
    mediana = margen.median()
    bajo = [t for t in por_tanque if margen[t] <= mediana]
    alto = [t for t in por_tanque if margen[t] > mediana]
    red = {t: por_tanque[t]["reduccion_absoluta"] for t in por_tanque}
    rb = float(np.mean([red[t] for t in bajo])) if bajo else float("nan")
    ra = float(np.mean([red[t] for t in alto])) if alto else float("nan")
    veredicto = ("mayor en los de bajo margen, como predice H1" if rb > ra else
                 "NO es mayor en los de bajo margen: no respalda esa parte de H1")
    return (f"- Lectura (calculada): reducción absoluta media {rb*100:.2f} pp en tanques de bajo margen "
            f"({', '.join(bajo)}) vs. {ra*100:.2f} pp en los de alto margen ({', '.join(alto)}); "
            f"es {veredicto}.\n")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="gemelo-tanques", description=__doc__)
    ap.add_argument("comando", choices=["todo"], nargs="?", default="todo")
    ap.add_argument("--config", type=Path, default=Path("config/escenario_base.yaml"))
    ap.add_argument("--salida", type=Path, default=Path("reports"))
    ap.add_argument("--datos", type=Path, default=Path("data/sintetico"))
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--meses", type=int, default=6)
    a = ap.parse_args(argv)
    a.salida.mkdir(parents=True, exist_ok=True)
    R = ejecutar_todo(a.config, a.salida, a.datos, a.seed, a.meses)
    print(f"OK. Resultados en {a.salida}/resumen_resultados.md (seed={R['seed']})")


if __name__ == "__main__":
    main()
