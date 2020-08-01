coverage:
	coverage erase
	coverage run --omit='.venv/*' -m unittest discover
	coverage report

test:
	python -m unittest discover

binary: coverage
	pyinstaller sbx/__main__.py -n sbx

format:
	isort .
	black -l 79 .
