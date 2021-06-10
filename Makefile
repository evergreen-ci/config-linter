test:
	poetry run pytest --flake8 --black --mypy --isort

test2:
	poetry run pytest --cache-clear --flake8 --black --mypy --isort

fix:
	poetry run black tests evergreen_lint

mypy:
	poetry run mypy -p evergreen_lint -p tests

publish:
	poetry build
	poetry publish

.PHONY: test test2 fix mypy
