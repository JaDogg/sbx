echo calculating coverage ....
mypy sbx
coverage erase
coverage run "--omit=.\.venv\*" --branch -m unittest discover
coverage report
coverage html -d .\coverage-report