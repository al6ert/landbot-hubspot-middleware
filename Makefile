.PHONY: start install

install:
	/usr/bin/python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

start:
	. .venv/bin/activate && uvicorn src.main:app --reload
