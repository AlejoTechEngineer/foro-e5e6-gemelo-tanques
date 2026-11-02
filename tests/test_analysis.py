import numpy as np
import pandas as pd

from gemelo_tanques import analysis as A


def test_fisher_y_reduccion():
    r = A.comparar_proporciones(30, 1000, 5, 1000)
    assert r["reduccion_absoluta"] > 0 and r["p_fisher"] < 0.001
    assert r["riesgo_relativo"] < 1


def test_sin_diferencia_no_es_significativa():
    r = A.comparar_proporciones(10, 500, 10, 500)
    assert r["p_fisher"] > 0.5


def test_caso_cero_eventos_no_rompe():
    r = A.comparar_proporciones(0, 100, 1, 100)
    assert np.isnan(r["riesgo_relativo"]) or r["riesgo_relativo"] >= 0


def test_tamano_muestra_monotono():
    assert A.tamano_muestra(0.03, 0.005) < A.tamano_muestra(0.03, 0.015)


def test_criterio_de_descarte_h2():
    """Si p(otra) <= p(vigilancia) la hipótesis se descarta (criterio del grupo)."""
    df = pd.DataFrame({
        "atencion": ["vigilancia"] * 100 + ["otra_actividad"] * 100,
        "desborde": [1] * 10 + [0] * 90 + [1] * 5 + [0] * 95,
    })
    assert A.diagnostico_d2(df)["H_descartada_por_criterio"] is True


def test_d1_signo_del_efecto(esc):
    from gemelo_tanques import simulation as S
    base = S.generar_base(esc, 60, np.random.default_rng(9))
    man = S.aplicar_modo(base, esc, "manual")
    assert A.diagnostico_d1(man)["odds_ratio_por_minuto_de_margen"] < 1


def test_mcnemar_conteos():
    m = np.array([1, 1, 1, 0, 0, 0])
    p = np.array([0, 0, 1, 0, 0, 1])
    r = A.mcnemar_pareado(m, p)
    assert r["desborda_solo_manual"] == 2 and r["desborda_solo_predictivo"] == 1
