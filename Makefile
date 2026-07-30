.PHONY: install test clean build binaries installer all tag release

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

VERSION ?= $(shell python3 -c "import sys; sys.path.insert(0,'.'); from md2tex import __version__; print(__version__)" 2>/dev/null || echo "0.1.0")

install: $(VENV)
	$(PIP) install -r requirements.txt

$(VENV):
	python3 -m venv $(VENV)

test: install
	$(PYTHON) -c "from md2tex.converter import parse, _render_block; t,f=parse('# Hola'); assert 'section' in _render_block(t,{},f); print('OK')"

clean:
	python3 build.py clean

build: clean
	python3 build.py binaries

installer:
	python3 build.py installer

all: clean
	python3 build.py all

tag:
	git tag -a v$(VERSION) -m "v$(VERSION)"
	git push origin v$(VERSION)

release: tag
	@echo "GitHub Actions se encarga del resto."
	@echo "Monitorea en: https://github.com/RafaelReyes0816/informe-latex/actions"
