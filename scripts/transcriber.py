#!/usr/bin/env python3
from whisper import load_model
from pathlib import Path
from datetime import datetime
from json import dump


class WhisperTranscriber:
    """Handles transcription using Whisper model"""
    
    def __init__(self, model_size="tiny", language="en", output_dir="data/transcripts"):
        """
        Initialize the WhisperTranscriber
        
        Args:
            model_size: Size of the Whisper model 
            language: Language code for transcription 
            output_dir: Directory to save transcripts
        """ 
        self.model_size = model_size
        self.language = language
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.model = None
        
    def load_model(self):
        """
        Load Whisper model
        """
        print(f"Loading Whisper {self.model_size} model...")
        self.model = load_model(self.model_size)
        print("Model loaded successfully!")
        
    def transcribe(self, audio_file, save=True) -> dict:
        """
        Transcribe audio file
        
        Args:
            audio_file: Path to audio file
            save: Whether to save transcript to file
            
        Returns:
            Dictionary with transcription results
        """
        if self.model is None:
            self.load_model()
            
        print(f"Transcribing {audio_file}...")
        result = self.model.transcribe(
            str(audio_file),
            language=self.language,
            verbose=False
        )
        
        if save:
            self._save_transcript(audio_file, result)
            
        return result
    
    def _save_transcript(self, audio_file, result):
        """
        Save transcript to file
        
        Args:
            audio_file: Path to audio file
            result: Transcription result dictionary
        """
        audio_path = Path(audio_file)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save text transcript
        txt_filename = f"transcript_{audio_path.stem}_{timestamp}.txt"
        txt_path = self.output_dir / txt_filename
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"Transcript - {datetime.now()}\n")
            f.write(f"Source: {audio_file}\n")
            f.write("-" * 50 + "\n\n")
            f.write(result["text"])
            
        # Save JSON with segments
        json_filename = f"transcript_{audio_path.stem}_{timestamp}.json"
        json_path = self.output_dir / json_filename
        
        with open(json_path, 'w', encoding='utf-8') as f:
            dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"Transcript saved to {txt_path}")
        
        return txt_path, json_path
    