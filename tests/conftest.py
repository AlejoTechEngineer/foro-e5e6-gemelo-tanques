from pathlib import Path

import pytest

from gemelo_tanques import config

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def esc():
    return config.cargar(RAIZ / "config" / "escenario_base.yaml")
