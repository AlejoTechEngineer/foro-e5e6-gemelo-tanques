import numpy as np
import pandas as pd

from gemelo_tanques import simulation as S


def test_calibracion_dentro_de_rangos_del_caso(esc):
    """El modo manual simulado reproduce las frecuencias observadas (tolerancia ±30 %)."""
    cal = S.tasa_mensual_esperada(esc, meses=240, seed=11)
    assert cal["dentro_de_rango"].all(), cal.to_string()


def test_determinismo_por_semilla(esc):
    a = S.generar_base(esc, 3, np.random.default_rng(5))
    b = S.generar_base(esc, 3, np.random.default_rng(5))
    pd.testing.assert_frame_equal(a, b)


def test_modo_invalido(esc):
    base = S.generar_base(esc, 1, np.random.default_rng(1))
    try:
        S.aplicar_modo(base, esc, "otro")
    except ValueError:
        return
    raise AssertionError("debió lanzar ValueError")


def test_manual_desborda_solo_si_retraso_supera_margen(esc):
    base = S.generar_base(esc, 6, np.random.default_rng(2))
    m = S.aplicar_modo(base, esc, "manual")
    esperado = (m["retraso_cierre_manual_min"] > m["margen_reaccion_min"]).astype(int)
    assert (m["desborde"] == esperado).all()
    assert (m.loc[m.desborde == 0, "volumen_desbordado_m3"] == 0).all()


def test_aviso_con_antelacion_suficiente_reduce_desbordes(esc):
    base = S.generar_base(esc, 120, np.random.default_rng(3))
    man = S.aplicar_modo(base, esc, "manual")["desborde"].mean()
    pre = S.aplicar_modo(base, esc, "predictivo", antelacion_min=8.0)["desborde"].mean()
    assert pre < 0.5 * man


def test_aviso_sin_antelacion_no_mejora(esc):
    """H2: un aviso que llega sin antelación no supera a la operación manual."""
    base = S.generar_base(esc, 120, np.random.default_rng(3))
    man = S.aplicar_modo(base, esc, "manual")["desborde"].mean()
    pre0 = S.aplicar_modo(base, esc, "predictivo", antelacion_min=0.0)["desborde"].mean()
    assert pre0 >= man * 0.95


def test_si_nadie_acusa_el_predictivo_equivale_al_manual(esc):
    base = S.generar_base(esc, 24, np.random.default_rng(4))
    man = S.aplicar_modo(base, esc, "manual")
    pre = S.aplicar_modo(base, esc, "predictivo", 6.0, p_acuse_vigilancia=0.0, p_acuse_otra=0.0)
    assert (man["desborde"].to_numpy() == pre["desborde"].to_numpy()).all()


def test_esquema_registro_comun(esc):
    base = S.generar_base(esc, 2, np.random.default_rng(6))
    reg = S.registro_comun(S.aplicar_modo(base, esc, "manual"))
    for c in ("fecha", "hora", "tanque", "atencion", "desborde", "duracion_desborde_min"):
        assert c in reg.columns
    assert set(reg["desborde"].unique()) <= {0, 1}
