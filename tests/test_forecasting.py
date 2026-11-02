from gemelo_tanques import forecasting as F


def test_holt_supera_referencia_simple_en_prueba(esc):
    """Hyndman & Athanasopoulos: el pronóstico debe superar la referencia simple en datos de prueba."""
    res, _ = F.evaluar(esc, n_por_tanque=40, seed=3)
    r5 = res[res.horizonte_min == 5.0].set_index("metodo")["rmse_min"]
    assert r5["holt"] < r5["balance"]


def test_traza_alcanza_objetivo(esc):
    import numpy as np
    t = esc.tanques["calderas"]
    tr = F.trazar_nivel(t, esc, 32.0, np.random.default_rng(1))
    assert tr.nivel_real[-1] >= esc.nivel_objetivo
    assert 25 < tr.t_objetivo_min < 45
