.PHONY: coverage test binary format docs

coverage:
	mypy sbx
	coverage erase
	coverage run --omit='.venv/*' --branch --source './sbx/' -m unittest discover
	coverage report
	coverage html -d ./coverage-report

test:
	mypy sbx
	python -m unittest discover

binary: coverage
	pyinstaller sbx/__main__.py -n sbx

format:
	isort .
	black -l 79 .

docs:
	pdoc3 --html --output-dir ../sbx_docs sbx --force
