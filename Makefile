.PHONY: run stop init build destroy

init:
	uv sync

run: init
	uv run uvicorn main:app --host 127.0.0.1 --port 8000

stop:
	@if lsof -t -i:8000; then \
		kill $(lsof -t -i:8000); \
	fi

build:
	docker build -t signal-vs-noise .
	docker run -d -p 8000:8000 --name signal-vs-noise-container signal-vs-noise
	@sleep 2
	@open http://127.0.0.1:8000

destroy:
	@docker stop signal-vs-noise-container || true
	@docker rm signal-vs-noise-container || true
	@docker rmi signal-vs-noise || true
