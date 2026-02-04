.PHONY: venv install install-dev run health cli clean test test-unit test-py

venv:
	python3 -m venv .venv

install:
	. .venv/bin/activate && python -m pip install --upgrade pip && pip install -r requirements.txt

install-dev:
	. .venv/bin/activate && python -m pip install --upgrade pip && pip install -r requirements-dev.txt

run:
	. .venv/bin/activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

health:
	curl http://127.0.0.1:8000/health

cli:
	. .venv/bin/activate && python cli.py "Security clearance required. US citizenship is required."

clean:
	rm -rf .venv

# Run unittest suite (smoke tests, etc.)
test-unit:
	. .venv/bin/activate && python -m unittest discover -s tests -t . -v

# Run pytest suite (parametrized rules tests + API integration tests)
test-py:
	. .venv/bin/activate && pytest -q

# Run all tests (matches CI intent)
test: test-unit test-py
