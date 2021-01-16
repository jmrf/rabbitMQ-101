.PHONY: clean test lint init check-readme

JOBS ?= 2

help:
	@echo "    install"
	@echo "        Install dependencies and download needed models."
	@echo "    clean"
	@echo "        Remove Python/build artifacts."
	@echo "    formatter"
	@echo "        Apply black formatting to code."
	@echo "    lint"
	@echo "        Lint code with flake8, and check if black formatter should be applied."
	@echo "    types"
	@echo "        Check for type errors using pytype."
	@echo "    pyupgrade"
	@echo "        Uses pyupgrade to upgrade python syntax."
	@echo "    test"
	@echo "        Run pytest on tests/."
	@echo "        Use the JOBS environment variable to configure number of workers (default: 1)."
	@echo "	   readme-toc"
	@echo "		   Generate a Table Of Content for the README.md"
	@echo "    tag"
	@echo "        Create tag based on the current version and push to remote."


install:
	pip install -r requirements.txt
	pip list

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f  {} +
	find . -name '__pycache__' -exec rm -r {} +
	find . -name 'README.md.*' -exec rm -f  {} +
	rm -rf build/
	rm -rf .pytype/
	rm -rf dist/

formatter:
	black .

lint:
	flake8 . --exclude tests/
	black --check . --exclude tests/

types: clean
	# https://google.github.io/pytype/
	pytype --keep-going rabbit101 --exclude rabbit101/tests

test: clean
	# OMP_NUM_THREADS can improve overral performance using one thread by process
	# (on tensorflow), avoiding overload
	OMP_NUM_THREADS=1 pytest tests -n $(JOBS) --cov rabbit101

readme-toc:
	# https://github.com/ekalinin/github-markdown-toc
	find . -name README.md -exec gh-md-toc --insert {} \;

tag:
	git tag $$( python -c 'import rabbit101; print(rabbit101.__version__)' )
	git push --tags

