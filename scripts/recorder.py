#!/usr/bin/env python3
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write, read
from datetime import datetime
from pathlib import Path



class AudioRecorder:
    """Handles audio recording from microphone"""
    
    def __init__(self, sample_rate=16000, channels=1, output_dir="data/recordings"):
        """
            Initialize the AudioRecorder

            Args: 
                sample_rate: Sample rate of the audio
                channels: Number of audio channels
                output_dir: Directory to save recordings
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def list_devices(self):
        """
            List available audio input devices
        """
        print("\nAvailable audio devices:")
        print(sd.query_devices())
        
    def set_device(self, device_id):
        """
            Set specific recording device

            Args:
                device_id: ID of the device to use for recording
        """
        self.device_id = device_id

    def record(self, duration_seconds=30, filename=None) -> Path:
        """
        Record audio for specified duration
        
        Args:
            duration_seconds: Recording duration in seconds
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to saved audio file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}"
            
        filepath = Path(self.output_dir / f"{filename}.wav")
        
        print(f"Recording for {duration_seconds} seconds...")
        recording = sd.rec(
            int(duration_seconds * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='int16',
            device=getattr(self, 'device_id', None)
        )
        sd.wait()
        
        write(str(filepath), self.sample_rate, recording)
        print(f"Recording saved to {filepath}")
        
        return filepath
    
    def continuous_record(self, chunk_duration=60, consolidate=True, callback=None, max_recordings=60):
        """
            Continuously record in chunks

            Args:
                chunk_duration: Duration of each chunk in seconds
                callback: Optional callback function to process each chunk
                         Signature: callback(audio_filepath)
        """
        chunk_num = 0
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"Starting continuous recording (Session: {session_id})... (Press Ctrl+C to stop)")
        
        try:
            while True:
                # Use session_id to group chunks together and avoid mixing with other sessions
                filename = f"chunk_{session_id}_{chunk_num:04d}"
                
                filepath = self.record(chunk_duration, filename)
                
                if callback:
                    callback(filepath)
                    
                chunk_num += 1
                print(f"Completed chunk {chunk_num}")
                
                if max_recordings and chunk_num >= max_recordings:
                    break
                
        except KeyboardInterrupt:
            print(f"\nRecording stopped. Total chunks: {chunk_num}")
            if consolidate:
                # Only consolidate chunks from THIS session
                pattern = f"chunk_{session_id}_*.wav"
                self._consolidate_recordings(pattern=pattern)

    def _consolidate_recordings(self, pattern="chunk_*.wav", output_filename=None, remove_chunks=True) -> Path:
        """
        Consolidate separate audio chunks into a single file
        
        Args:
            pattern: Glob pattern to match chunks to consolidate
            output_filename: Name of the output file
            remove_chunks: Whether to delete individual chunks after consolidation

        Returns:
            Path to the consolidated audio file
        """
        chunks = sorted(self.output_dir.glob(pattern))
        if not chunks:
            print("No chunks found to consolidate")
            return
            
        print(f"Found {len(chunks)} chunks to consolidate...")
        
        # Read all chunks
        data_list = []
        sample_rate = None
        
        for chunk_path in chunks:
            sr, data = read(str(chunk_path))
            if sample_rate is None:
                sample_rate = sr
            elif sr != sample_rate:
                print(f"Warning: Sample rate mismatch in {chunk_path}")
            
            data_list.append(data)
            
        if not data_list:
            return
            
        # Concatenate
        combined_data = np.concatenate(data_list)
        
        # Determine output filename
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"consolidated_{timestamp}.wav"
            
        output_path = Path(self.output_dir / output_filename)
        
        # Write consolidated file
        write(str(output_path), sample_rate, combined_data)
        print(f"Consolidated recording saved to {output_path}")
        
        # Cleanup
        if remove_chunks:
            for chunk_path in chunks:
                chunk_path.unlink()
            print("Removed individual chunk files")
            
        return output_path