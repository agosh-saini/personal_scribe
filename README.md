# Personal Scribe

Personal Scribe is a Python-based tool for continuous audio recording and
automatic transcription using OpenAI's Whisper model.

NEXT STEPS:

- ADDING TRANCRIPTION OF AUDIO COMING INTO THE SPEAKERS

## Prerequisites

- Python 3.8+
- [FFmpeg](https://ffmpeg.org/) (Required for Whisper/Audio processing)
  ```bash
  # macOS
  brew install ffmpeg
  ```

## Installation

1. Clone the repository or download the source code.
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the main application:

```bash
python main.py
```

- The application will start recording immediately.
- Transcripts (TXT and JSON) are saved to `data/transcripts`.
- Raw recordings are saved to `data/recordings`.
- Press `Ctrl+C` to stop the recording session. The application will stop
  recording and consolidate the audio chunks.

## Configuration

You can customize the behavior by editing `config/config.yaml`:

```yaml
audio:
    sample_rate: 16000
    chunk_duration: 60

model:
    base_model: "tiny"
    language: "en"
```

## License

MIT License
