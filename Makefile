.PHONY: help format lint test coverage all clean build

PYTHON := python3
SRC_DIR := taskcrafter
TEST_DIR := tests
ENTRY_POINT := main.py
APP_NAME := taskcrafter

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install    Install dependencies"
	@echo "  lint       Run flake8"
	@echo "  test       Run tests with pytest"
	@echo "  coverage   Run tests and show coverage"
	@echo "  build      Build standalone binary with PyInstaller"
	@echo "  all        Run format, lint and test"
	@echo "  clean      Remove temporary files and build artifacts"
	@echo "  docker     Build and run container (use CONTAINER_TOOL to specify podman or docker)"

install:
	@echo "Installing dependencies..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

lint:
	flake8 $(SRC_DIR) $(TEST_DIR)

test:
	pytest $(TEST_DIR)

coverage:
	pytest --cov=$(SRC_DIR) --cov-report=term-missing --cov-report html $(TEST_DIR)

build:
	pyinstaller taskcrafter.spec

all: format lint test

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	rm -rf .pytest_cache .mypy_cache .coverage dist build *.spec

docker:
	@if [ -z "$(CONTAINER_TOOL)" ]; then \
		if command -v podman >/dev/null 2>&1; then \
			@echo "Using Podman as the container tool"; \
			CONTAINER_TOOL=podman; \
		else \
			@echo "Using Docker as the container tool"; \
			CONTAINER_TOOL=docker; \
		fi; \
	fi; \
	$$CONTAINER_TOOL build -t $(APP_NAME) .; \
	@echo "Container for $(APP_NAME) built and run successfully using $$CONTAINER_TOOL."
	@echo "You can now access the application in the container."
