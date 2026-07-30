.PHONY: install test clean build release tag

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYINSTALLER = $(VENV)/bin/pyinstaller

VERSION ?= 0.1.0

install: $(VENV)
	$(PIP) install -r requirements.txt

$(VENV):
	python3 -m venv $(VENV)

test: install
	$(PYTHON) -c "from md2tex.converter import parse, _render_block; t, f = parse('# Hola'); assert 'section' in _render_block(t, {}, f); print('OK')"

clean:
	rm -rf build/ dist/ *.spec
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache

build: install
	$(PIP) install pyinstaller
	$(PYINSTALLER) --onefile \
		--name md2tex \
		--add-data "templates:templates" \
		--noconsole \
		md2tex/__main__.py

build-cli: install
	$(PIP) install pyinstaller
	$(PYINSTALLER) --onefile \
		--name md2tex-cli \
		--add-data "templates:templates" \
		md2tex/__main__.py

dist: build build-cli
	@echo "Builds listos en dist/"

tag:
	git tag -a v$(VERSION) -m "v$(VERSION)"
	git push origin v$(VERSION)

release: tag
	@echo "Crea el release en: https://github.com/RafaelReyes0816/informe-latex/releases/new"
