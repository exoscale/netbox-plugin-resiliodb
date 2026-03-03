format:
	uv run ruff format .

lint:
	uv run ruff check --select I --fix
	uv run ruff check --fix .

check-lint:
	uv run ruff check --select I
	uv run ruff check .

check-format:
	uv run ruff format --check .
