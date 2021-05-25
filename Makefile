all:

test:
	poetry run pytest --flake8 --black --mypy --isort
	poetry run itest

test2:
	poetry run pytest --cache-clear --flake8 --black --mypy --isort
	poetry run itest

fix:
	poetry run black tests evergreen_lint

mypy:
	poetry run mypy -p evergreen_lint -p tests

.PHONY: test test2 fix mypy
