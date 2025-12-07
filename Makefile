.PHONY: install run build publish package-install lint format

install:
	poetry install

run:
	poetry run python main.py

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python -m pip install dist/*.whl

lint:
	poetry run ruff check .

format:
	poetry run ruff format .