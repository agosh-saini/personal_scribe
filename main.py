#!/usr/bin/env python3
import yaml
from pathlib import Path

from scripts.recorder import AudioRecorder
from scripts.transcriber import WhisperTranscriber


class WhisperNotetaker:
    """Main application class for audio recording and transcription"""
    
    def __init__(self, config_path="config/config.yaml"):
        """
        Initialize the WhisperNotetaker application
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        # Initialize components
        self.recorder = AudioRecorder(
            sample_rate=self.config['audio']['sample_rate'],
            channels=self.config['audio']['channels'],
            output_dir=self.config['paths']['recordings'],
            device=self.config['model'].get('device')
        )
        
        self.transcriber = WhisperTranscriber(
            model_size=self.config['model']['size'],
            language=self.config['model']['language'],
            output_dir=self.config['paths']['transcripts']
        )
        
    def show_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("           WHISPER NOTETAKER")
        print("="*60)
        print("  1. List audio devices")
        print("  2. Set recording device")
        print("  3. Test BlackHole setup (10s)")
        print("  4. Start recording session (max 1hr)")
        print("  5. View all recordings")
        print("  6. Transcribe a recording")
        print("  7. View all transcripts")
        print("  8. Delete a recording")
        print("  0. Exit")
        print("="*60)
        
    def run(self):
        """Main application loop"""
        while True:
            self.show_menu()
            choice = input("\nEnter choice: ").strip()
            
            try:
                if choice == "1":
                    self._list_devices()
                    
                elif choice == "2":
                    self._set_device()
                    
                elif choice == "3":
                    self._test_audio_setup()
                    
                elif choice == "4":
                    self._start_recording_session()
                    
                elif choice == "5":
                    self._view_recordings()
                    
                elif choice == "6":
                    self._transcribe_recording()
                    
                elif choice == "7":
                    self._view_transcripts()
                    
                elif choice == "8":
                    self._delete_recording()
                    
                elif choice == "0":
                    print("\n👋 Goodbye!")
                    break
                    
                else:
                    print("❌ Invalid choice! Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Operation cancelled by user")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                
    def _list_devices(self):
        """List available audio devices"""
        self.recorder.list_devices()
        
    def _set_device(self):
        """Set recording device"""
        device_id = input("Enter device ID: ").strip()
        try:
            self.recorder.set_device(int(device_id))
            print("✅ Device set successfully!")
        except ValueError:
            print("❌ Invalid device ID")
    
    def _test_audio_setup(self):
        """Test BlackHole recording setup"""
        print("\n" + "="*60)
        print("AUDIO SETUP TEST")
        print("="*60)
        print("\n📋 Instructions:")
        print("   1. Ensure 'Multi-Output Device' (w/ BlackHole) is set as system output")
        print("   2. Play some audio/video/music on your Mac")
        print("   3. Recording will capture for 10 seconds")
        print("   4. We'll transcribe to verify it worked\n")
        
        input("Press Enter when ready to start test...")
        
        print("\n🎙️  Recording 10-second test...")
        print("▶️  PLAY AUDIO NOW (YouTube, Spotify, etc.)\n")
        
        filepath = self.recorder.record(duration_seconds=10, filename="test_blackhole")
        
        print(f"\n✅ Test recording saved: {filepath}")
        print("\n🔄 Transcribing to verify audio capture...")
        
        result = self.transcriber.transcribe(filepath)
        
        print("\n" + "="*60)
        print("CAPTURED AUDIO (Transcription):")
        print("="*60)
        print(result['text'] if result['text'].strip() else "❌ NO AUDIO DETECTED")
        print("="*60)
        
        if result['text'].strip():
            print("\n✅ SUCCESS! BlackHole is capturing system audio")
        else:
            print("\n❌ FAILED - No audio captured. Check your setup:")
            print("   1. Is 'Multi-Output Device' set as system output?")
            print("   2. Did you play audio during the test?")
            print("   3. Is BlackHole (or Aggregate Device) selected as input?")
        
        # Offer to delete test file
        delete = input("\nDelete test file? (y/n): ").lower().strip()
        if delete == 'y':
            filepath.unlink()
            print("🗑️  Test file deleted")
            
    def _start_recording_session(self):
        """Start continuous recording session with auto-consolidation"""
        print("\n" + "="*60)
        print("RECORDING SESSION")
        print("="*60)
        
        # Get chunk duration
        chunk_duration = input(f"Chunk duration in seconds (default {self.config['audio']['chunk_duration']}): ").strip()
        chunk_duration = int(chunk_duration) if chunk_duration else self.config['audio']['chunk_duration']
        
        # Calculate max recording time (1 hour = 3600 seconds)
        max_duration = 3600
        max_chunks = max_duration // chunk_duration
        
        print(f"\n📝 Configuration:")
        print(f"   - Chunk duration: {chunk_duration} seconds")
        print(f"   - Maximum recording: 1 hour ({max_chunks} chunks)")
        print(f"   - Output: Single consolidated file")
        print(f"\n💡 TIP: Minimize this window and start your meeting/call")
        print("⚠️  Press Ctrl+C when done to stop and consolidate\n")
        
        input("Press Enter to start recording...")
        
        # Start recording
        self.recorder.continuous_record(
            chunk_duration=chunk_duration,
            consolidate=True,
            callback=None
        )
        
        print("\n✅ Recording session complete!")
        
        # Ask if user wants to transcribe now
        transcribe = input("\n📝 Transcribe now? (y/n): ").lower().strip()
        if transcribe == 'y':
            # Find the most recent consolidated file
            recordings_path = Path(self.config['paths']['recordings'])
            consolidated_files = sorted(
                recordings_path.glob("consolidated_*.wav"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            if consolidated_files:
                latest = consolidated_files[0]
                print(f"\n🔄 Transcribing: {latest.name}")
                print("⏳ This may take a while for long recordings...\n")
                
                result = self.transcriber.transcribe(latest)
                
                print("\n" + "="*60)
                print("TRANSCRIPT PREVIEW:")
                print("="*60)
                preview_length = 500
                if len(result['text']) > preview_length:
                    print(result['text'][:preview_length] + "...")
                    print(f"\n(Showing first {preview_length} characters)")
                else:
                    print(result['text'])
                print("="*60)
                print(f"\n✅ Full transcript saved to transcripts folder")
            else:
                print("❌ No consolidated file found")
                
    def _view_recordings(self):
        """View all recordings"""
        recordings_path = Path(self.config['paths']['recordings'])
        recordings = sorted(
            recordings_path.glob("consolidated_*.wav"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not recordings:
            print("\n❌ No recordings found.")
            print("💡 Use option 4 to create a recording session")
            return
            
        print("\n" + "="*60)
        print(f"ALL RECORDINGS ({len(recordings)} total)")
        print("="*60)
        
        for i, rec in enumerate(recordings, 1):
            size_mb = rec.stat().st_size / 1024 / 1024
            timestamp = rec.stem.replace('consolidated_', '')
            
            print(f"\n  {i}. {rec.name}")
            print(f"     Size: {size_mb:.2f} MB")
            print(f"     Created: {timestamp}")
                
    def _transcribe_recording(self):
        """Transcribe a recording"""
        recordings_path = Path(self.config['paths']['recordings'])
        recordings = sorted(
            recordings_path.glob("consolidated_*.wav"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not recordings:
            print("\n❌ No recordings found.")
            return
            
        print("\n" + "="*60)
        print("SELECT RECORDING TO TRANSCRIBE")
        print("="*60)
        
        for i, rec in enumerate(recordings, 1):
            size_mb = rec.stat().st_size / 1024 / 1024
            timestamp = rec.stem.replace('consolidated_', '')
            print(f"  {i}. {timestamp} ({size_mb:.2f} MB)")
            
        choice = input("\nEnter number: ").strip()
        
        try:
            selected = recordings[int(choice) - 1]
            print(f"\n🔄 Transcribing: {selected.name}")
            print("⏳ This may take a while for long recordings...\n")
            
            result = self.transcriber.transcribe(selected)
            
            print("\n" + "="*60)
            print("TRANSCRIPT PREVIEW:")
            print("="*60)
            preview_length = 500
            if len(result['text']) > preview_length:
                print(result['text'][:preview_length] + "...")
                print(f"\n(Showing first {preview_length} characters)")
            else:
                print(result['text'])
            print("="*60)
            print(f"\n✅ Full transcript saved to transcripts folder")
            
            # Offer to delete recording after transcription
            delete = input("\nDelete this recording? (y/n): ").lower().strip()
            if delete == 'y':
                selected.unlink()
                print(f"🗑️  Deleted {selected.name}")
            
        except (IndexError, ValueError):
            print("❌ Invalid selection")
            
    def _view_transcripts(self):
        """View all transcripts"""
        transcripts_path = Path(self.config['paths']['transcripts'])
        transcripts = sorted(
            transcripts_path.glob("*.txt"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not transcripts:
            print("\n❌ No transcripts found.")
            return
            
        print("\n" + "="*60)
        print(f"ALL TRANSCRIPTS ({len(transcripts)} total)")
        print("="*60)
        
        for i, trans in enumerate(transcripts, 1):
            print(f"  {i}. {trans.name}")
            
        choice = input("\nEnter number to view full transcript (or press Enter to skip): ").strip()
        
        if choice.isdigit():
            try:
                filepath = transcripts[int(choice) - 1]
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                print("\n" + "="*60)
                print(content)
                print("="*60)
                
                # Offer to delete
                delete = input("\nDelete this transcript? (y/n): ").lower().strip()
                if delete == 'y':
                    filepath.unlink()
                    # Also delete corresponding JSON
                    json_file = filepath.with_suffix('.json')
                    if json_file.exists():
                        json_file.unlink()
                    print(f"🗑️  Deleted {filepath.name}")
                    
            except (IndexError, ValueError):
                print("❌ Invalid selection")
    
    def _delete_recording(self):
        """Delete a recording file"""
        recordings_path = Path(self.config['paths']['recordings'])
        recordings = sorted(
            recordings_path.glob("consolidated_*.wav"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not recordings:
            print("\n❌ No recordings found.")
            return
            
        print("\n" + "="*60)
        print("SELECT RECORDING TO DELETE")
        print("="*60)
        
        for i, rec in enumerate(recordings, 1):
            size_mb = rec.stat().st_size / 1024 / 1024
            timestamp = rec.stem.replace('consolidated_', '')
            print(f"  {i}. {timestamp} ({size_mb:.2f} MB)")
            
        choice = input("\nEnter number (or press Enter to cancel): ").strip()
        
        if choice.isdigit():
            try:
                selected = recordings[int(choice) - 1]
                confirm = input(f"\n⚠️  Delete {selected.name}? (y/n): ").lower().strip()
                
                if confirm == 'y':
                    selected.unlink()
                    print(f"🗑️  Deleted {selected.name}")
                else:
                    print("Cancelled")
                    
            except (IndexError, ValueError):
                print("❌ Invalid selection")


if __name__ == "__main__":
    app = WhisperNotetaker()
    app.run()