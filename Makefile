# Variables
MAINFILE = main.py
OUTPUT_DIR = dist
PYINSTALLER = pyinstaller

# Default target
all: build

# Build the executable using pyinstaller
build:
	$(PYINSTALLER) --onefile $(MAINFILE)

# Clean up build artifacts
clean:
	rm -rf $(OUTPUT_DIR) build *.spec

# Run the Python script
run:
	python3 $(MAINFILE)

# Install dependencies
install:
	pip install -r requirements.txt

# Help message
help:
	@echo "Available targets:"
	@echo "  build     - Build the executable using pyinstaller"
	@echo "  clean     - Remove build artifacts"
	@echo "  run       - Run the Python script"
	@echo "  install   - Install dependencies from requirements.txt"
	@echo "  help      - Show this help message"