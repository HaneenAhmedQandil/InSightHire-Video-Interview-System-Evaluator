## without cleaning
import whisper
import os
import tempfile

class Transcription:
    def __init__(self, model_name="large"):
        """Initialize Whisper model for transcription"""
        try:
            self.model = whisper.load_model(model_name)
            print(f"Whisper model '{model_name}' loaded successfully")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            raise
    
    def transcribe_audio(self, audio_path, language="en"):
        """Transcribe audio file to text"""
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            print(f"Transcribing audio: {audio_path}")
            
            # Force English language and add other parameters for better accuracy
            result = self.model.transcribe(
                audio_path,
                language="en",  # Force English
                task="transcribe",  # Not translate
                verbose=False,
                word_timestamps=False,
                temperature=0.0,  # More deterministic
                no_speech_threshold=0.6,  # Adjust silence detection
                logprob_threshold=-1.0,
                compression_ratio_threshold=2.4
            )
            
            transcript = result["text"].strip()
            
            # Return transcript as-is without cleaning (for grammar checker to handle filler words)
            print(f"Transcription completed. Length: {len(transcript)} characters")
            return transcript
            
        except Exception as e:
            print(f"Error during transcription: {e}")
            return f"Transcription failed: {str(e)}"
    
    def _clean_transcript(self, text):
        """Clean up the transcript text - MINIMAL CLEANING ONLY"""
        import re
        
        # Only remove multiple spaces (keep everything else as-is)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Basic quality check for extremely poor audio
        words = text.split()
        if len(words) > 10:
            # Only flag if more than 80% of words are identical (extreme repetition)
            unique_words = set(words)
            if len(unique_words) / len(words) < 0.2:
                return "Audio quality too poor for reliable transcription"
        
        return text.strip()
    
    def transcribe_video(self, video_path):
        """Extract audio from video and transcribe"""
        try:
            # Create temporary audio file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio_path = temp_audio.name
            
            # Extract audio using ffmpeg
            import subprocess
            
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-vn',  # no video
                '-acodec', 'pcm_s16le',
                '-ar', '16000',  # 16kHz for Whisper
                '-ac', '1',  # mono
                '-af', 'volume=2.0',  # Boost volume
                temp_audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {result.stderr}")
            
            # Transcribe the extracted audio
            transcript = self.transcribe_audio(temp_audio_path, language="en")
            
            # Clean up temp file
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
            
            return transcript
            
        except Exception as e:
            print(f"Error transcribing video: {e}")
            return f"Video transcription failed: {str(e)}"