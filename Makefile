coverage:
	coverage erase
	coverage run --omit='.venv/*' -m unittest discover
	coverage report

test:
	python -m unittest discover

binary: coverage
	pyinstaller sbx/sbx_main.py -n sbx

format:
	isort .
	black -l 79 .
