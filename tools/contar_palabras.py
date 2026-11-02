"""Cuenta las palabras de la publicación SIN referencias ni encabezado de portada (rúbrica: 600-900)."""
import re
import sys
from pathlib import Path

texto = Path(sys.argv[1]).read_text(encoding="utf-8")
# Se excluye todo lo que sigue a '## Referencias' y los comentarios HTML de ayuda.
texto = texto.split("## Referencias")[0]
texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
texto = re.sub(r"[#*`>|_\-]", " ", texto)
palabras = re.findall(r"\b[\wáéíóúüñÁÉÍÓÚÜÑ%.,/()-]+\b", texto)
n = len(palabras)
estado = "OK" if 600 <= n <= 900 else "FUERA DE RANGO (600-900)"
print(f"{n} palabras (sin referencias) -> {estado}")
sys.exit(0 if 600 <= n <= 900 else 1)
