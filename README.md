# Audio Transcription Tool

A Python-based tool for transcribing M4A audio files to text. Includes both command-line and GUI interfaces.

## Prerequisites

- macOS with Homebrew installed
- Git

## Quick Start
```bash
git clone <repository-url>
cd transcribe
make install
```

## Detailed Installation

If you prefer to install components manually:

1. Install ffmpeg (on macOS):
```bash
brew install ffmpeg
```

2. Install tkinter (on macOS):
```bash
brew install python-tk@3.13
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### GUI Version
Run the graphical interface:
```bash
make run-gui
```
or
```bash
python transcribe_ui.py
```

### Command-Line Version
To transcribe a single audio file:
```bash
make run-cli FILE=path/to/your/audio.m4a
```
or
```bash
python transcribe.py path/to/your/audio.m4a
```

The GUI provides an easy-to-use interface where you can:
- Select an M4A audio file using the file browser
- Click "Transcribe" to start the transcription process
- View the transcribed text in the application window
- Save the transcription to a text file

## Dependencies
The following Python packages are required:
- SpeechRecognition 3.10.1 - For audio-to-text conversion
- pydub 0.25.1 - For audio file processing

## Troubleshooting

If you encounter any issues:

1. Ensure ffmpeg is properly installed:
```bash
ffmpeg -version
```

2. Verify Python version:
```bash
python --version
```

3. Check if all dependencies are installed:
```bash
pip list | grep -E "SpeechRecognition|pydub"
```

## License

[Add license information here]
