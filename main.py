#!/usr/bin/env python3
import yaml
import sys
from pathlib import Path
from scripts.recorder import AudioRecorder
from scripts.transcriber import WhisperTranscriber

def load_config(config_path="config/config.yaml"):
    """Load configuration from YAML file"""
    path = Path(config_path)
    if not path.exists():
        print(f"Error: Config file not found at {path}")
        sys.exit(1)
        
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    # Load configuration
    config = load_config()
    
    # Initialize Recorder
    print("Initializing Audio Recorder...")
    try:
        recorder = AudioRecorder(
            sample_rate=config['audio']['sample_rate'],
            channels=config['audio']['channels'],
            output_dir=config['paths']['recordings']
        )
    except Exception as e:
        print(f"Failed to initialize recorder: {e}")
        sys.exit(1)

    # Initialize Transcriber
    print("Initializing Whisper Transcriber...")
    try:
        transcriber = WhisperTranscriber(
            model_size=config['model']['base_model'],
            language=config['model']['language'],
            output_dir=config['paths']['transcripts']
        )
    except Exception as e:
        print(f"Failed to initialize transcriber: {e}")
        sys.exit(1)

    def process_chunk(audio_path):
        """Callback to transcribe audio chunk immediately after recording"""
        try:
            print(f"\nProcessing chunk: {audio_path.name}")
            transcriber.transcribe(audio_path)
        except Exception as e:
            print(f"Error transcribing {audio_path}: {e}")

    # Start Recording Loop
    print("\n" + "="*50)
    print(f"Starting Personal Scribe")
    print(f"Chunk Duration: {config['audio']['chunk_duration']}s")
    print("Press Ctrl+C to stop recording")
    print("="*50 + "\n")

    try:
        recorder.continuous_record(
            chunk_duration=config['audio']['chunk_duration'],
            consolidate=True,
            callback=process_chunk
        )
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
