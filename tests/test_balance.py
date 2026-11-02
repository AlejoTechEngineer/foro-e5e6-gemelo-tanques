import math

import pytest

from gemelo_tanques import balance


def test_margen_conocido():
    # 30 m3, 10 % = 3 m3, a 30 m3/h -> 0.1 h = 6 min
    assert balance.margen_reaccion_min(30, 30) == pytest.approx(6.0)


def test_margen_con_consumo_y_sin_neto():
    assert balance.margen_reaccion_min(30, 30, consumo_m3h=15) == pytest.approx(12.0)
    assert math.isinf(balance.margen_reaccion_min(30, 10, consumo_m3h=10))


def test_orden_de_margenes_del_caso(esc):
    """H1 diagnóstica: Calderas y Compresores tienen el menor margen; Auxiliar el mayor."""
    tabla = balance.tabla_margenes(esc.tanques)
    nombres = [f["tanque"] for f in tabla]
    assert set(nombres[:2]) == {"calderas", "compresores"}
    assert nombres[-1] == "auxiliar"


def test_duracion_llenado():
    assert balance.duracion_llenado_min(30, 30, 0.3, 0.9) == pytest.approx(36.0)
