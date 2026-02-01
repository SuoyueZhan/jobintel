.PHONY: venv install run health cli clean test

venv:
	python3 -m venv .venv

install:
	. .venv/bin/activate && pip install -r requirements.txt

run:
	. .venv/bin/activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

health:
	curl http://127.0.0.1:8000/health

cli:
	. .venv/bin/activate && python cli.py "Security clearance required. US citizenship is required."

clean:
	rm -rf .venv
test:
	. .venv/bin/activate && python -m tests.smoke_test

