.PHONY: test api demo doctor run clean

test:
	pytest -q

api:
	uvicorn cinefactory.api.app:app --reload --host 127.0.0.1 --port 8765

doctor:
	cinefactory doctor

demo:
	python scripts/demo_vertical_slice.py

run:
	cinefactory run --prompt "Create a realistic family drama about a hidden sacrifice" --profile family_drama --production-mode slate --tts-mode espeak --no-master-4k

clean:
	rm -rf .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
