.PHONY: install test lint run words
install:
	pip install -e ".[dev]"
test:
	pytest
lint:
	ruff check src tests
run:
	python -m gemelo_tanques
words:
	python tools/contar_palabras.py docs/01_publicacion_foro.md
