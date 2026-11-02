from pathlib import Path

from gemelo_tanques.cli import ejecutar_todo

RAIZ = Path(__file__).resolve().parents[1]


def test_pipeline_completo_y_reproducible(tmp_path):
    cfg = RAIZ / "config" / "escenario_base.yaml"
    r1 = ejecutar_todo(cfg, tmp_path / "a", tmp_path / "da", seed=42)
    r2 = ejecutar_todo(cfg, tmp_path / "b", tmp_path / "db", seed=42)
    assert r1["h1_global"]["p_referencia"] == r2["h1_global"]["p_referencia"]
    assert (tmp_path / "a" / "resumen_resultados.md").exists()
    assert "DATOS SINTÉTICOS" in (tmp_path / "a" / "resumen_resultados.md").read_text(encoding="utf-8")
    assert (tmp_path / "a" / "figures" / "fig5_sensibilidad.png").exists()
    assert "decision" in r1["h2"]
    assert "Lectura (calculada)" in (tmp_path / "a" / "resumen_resultados.md").read_text(encoding="utf-8")
