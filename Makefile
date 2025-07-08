# see https://makefiletutorial.com/

SHELL := /bin/bash -eu -o pipefail
PROJ_NAME := kleinanzeigen.de

CMD_CIUR_FOLLOW_PERSON := $(PROJ_NAME)-follow-person
CMD_CIUR_SEARCH_ALL := $(PROJ_NAME)-search-all

update_pip_and_wheel:
	pip install -U pip wheel

install_prod:
	pip install  '.'
	opentelemetry-bootstrap -a install

install_dev:
	pip install -e '.[dev]'
	opentelemetry-bootstrap -a install

wheel:
	pip install build twine
	python -m build . --wheel

isort:
	isort src tests $${ARGS:-}

pylint:
	pylint src tests

coverage_run:
	coverage run -m pytest -m 'not integration'

coverage_report:
	coverage report

coverage_report_html:
	coverage html

coverage: coverage_run coverage_report

pytest_integration:
	pytest -m 'integration' -vv

mypy:
	mypy src

pip-audit:
	pip-audit --ignore-vuln=PYSEC-2022-42969

markdownlint:
	markdownlint .

code_check: \
	isort \
	pylint \
	coverage_run coverage_report \
	mypy \
	pip-audit \
	markdownlint

run:
	$(CMD_CIUR_FOLLOW_PERSON) && $(CMD_CIUR_SEARCH_ALL)
