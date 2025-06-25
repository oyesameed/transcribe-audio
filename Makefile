.PHONY: install run-gui run-cli

install:
	@echo "Installing dependencies..."
	@command -v brew >/dev/null 2>&1 || { echo "Homebrew is required. Please install it first."; exit 1; }
	@command -v ffmpeg >/dev/null 2>&1 || brew install ffmpeg
	@command -v python3 >/dev/null 2>&1 || brew install python@3.13
	@brew install python-tk@3.13 || true
	@pip install -r requirements.txt
	@echo "Installation complete!"

run-gui:
	@python transcribe_ui.py

run-cli:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make run-cli FILE=path/to/audio.m4a"; \
		exit 1; \
	fi
	@python transcribe.py $(FILE)
