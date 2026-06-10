.PHONY: install dev test setup lint

install:
	pip install -r requirements.txt

dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --tb=short

setup:
	bash scripts/install_ollama.sh
	python -c "import chromadb; print('ChromaDB OK')"

lint:
	ruff check . && mypy .
