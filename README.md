# Personal Scribe

Personal Scribe is a Python-based tool for continuous audio recording and
automatic transcription using OpenAI's Whisper Tiny model.

# Next Steps

Testing using an actual call to see if it works.

## System Audio Recording Setup (BlackHole)

To record system audio (what you hear: Zoom, YouTube, etc.) and optionally your
microphone at the same time, follow these steps:

### 1. Install BlackHole

Recommended for macOS (free).

```bash
brew install blackhole-2ch
```

### 2. Audio MIDI Setup

1. Open **Audio MIDI Setup** (search in Spotlight).
2. **Create Multi-Output Device** (for hearing audio while recording):
   - Click `+` → **Create Multi-Output Device**.
   - Check **BlackHole 2ch**.
   - Check your **Headphones/Speakers**.
   - _Set this Multi-Output Device as your mac's system output in Sound
     Settings._
3. **Create Aggregate Device** (to capture Mic + System Audio):
   - Click `+` → **Create Aggregate Device**.
   - Check **BlackHole 2ch**.
   - Check your **Microphone**.
   - _Select this Aggregate Device (or just BlackHole if you only want system
     audio) in the application._

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
  chunk_duration: 10

model:
  base_model: "tiny"
  language: "en"
```

## License

MIT License
