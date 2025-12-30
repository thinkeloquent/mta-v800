.PHONY: install start dev

install:
	cd .. && poetry install

start:
	cd .. && poetry run python examples/basic_usage.py

dev:
	cd .. && poetry run uvicorn examples.fastapi_app.main:app --reload
