import os
import subprocess
import pickle
import numpy as np
import librosa
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import load_model
from collections import Counter

class EmotionAnalyzer:
    def __init__(self, model_path, scaler_path, encoder_path):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.encoder_path = encoder_path
        self.model = self.load_model()
        self.scaler = self.load_scaler()
        self.encoder = self.load_encoder()
        self.n_mfcc = 40
        self.max_frames = 100

    def load_model(self):
        """Load the pre-trained emotion classification model"""
        return load_model(self.model_path)

    def load_scaler(self):
        """Load the StandardScaler"""
        with open(self.scaler_path, 'rb') as f:
            return pickle.load(f)

    def load_encoder(self):
        """Load the label encoder"""
        with open(self.encoder_path, 'rb') as f:
            return pickle.load(f)

    def extract_audio(self, video_path, output_path="temp_audio.wav"):
        """Extract audio from the video file"""
        try:
            # Make sure the video file exists
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Use absolute paths
            video_path = os.path.abspath(video_path)
            output_path = os.path.abspath(output_path)
            
            cmd = [
                'ffmpeg', '-y',  # -y to overwrite output files
                '-i', video_path,
                '-vn',           # no video
                '-acodec', 'pcm_s16le',  # audio codec
                '-ar', '16000',  # 16 kHz sampling
                '-ac', '1',      # mono
                output_path
            ]
            
            print(f"Extracting audio from: {video_path}")
            print(f"Output audio to: {output_path}")
            
            res = subprocess.run(cmd, capture_output=True, text=True)
            
            if res.returncode == 0 and os.path.exists(output_path):
                print(f"Audio extraction successful: {output_path}")
                return output_path
            else:
                print(f"FFmpeg error: {res.stderr}")
                raise RuntimeError(f"Failed to extract audio from video. FFmpeg error: {res.stderr}")
                
        except FileNotFoundError as e:
            raise RuntimeError(f"FFmpeg not found. Please install FFmpeg: {e}")
        except Exception as e:
            raise RuntimeError(f"Audio extraction failed: {e}")


    def pad_truncate(self, feat: np.ndarray, max_len: int) -> np.ndarray:
        """Pad or truncate features to fixed length"""
        if feat.shape[1] < max_len:
            return np.pad(feat, ((0,0),(0,max_len-feat.shape[1])), mode='constant')
        else:
            return feat[:, :max_len]

    def extract_features_fixed(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Extract fixed-length features from audio"""
        if y.size == 0:
            return np.zeros((self.n_mfcc+2)*self.max_frames)
        
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)
        mfcc = self.pad_truncate(mfcc, self.max_frames)
        mfcc = (mfcc - mfcc.mean())/(mfcc.std()+1e-6)
        
        zcr = self.pad_truncate(librosa.feature.zero_crossing_rate(y=y), self.max_frames)
        rms = self.pad_truncate(librosa.feature.rms(y=y), self.max_frames)
        
        return np.vstack((mfcc, zcr, rms)).flatten()

    def add_noise(self, x):
        return x + 0.035*np.random.uniform()*np.max(x)*np.random.normal(size=x.shape)

    def stretch(self, x, rate=0.8):
        return librosa.effects.time_stretch(y=x, rate=rate)

    def shift(self, x):
        return np.roll(x, int(np.random.uniform(-5,5)*1000))

    def pitch(self, x, sr, steps=0.7):
        return librosa.effects.pitch_shift(y=x, sr=sr, n_steps=steps)

    def get_features_from_wave(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Extract augmented features from audio wave"""
        feats = [self.extract_features_fixed(y, sr)]
        
        # Add augmented versions
        feats.append(self.extract_features_fixed(self.add_noise(y), sr))
        feats.append(self.extract_features_fixed(self.stretch(y, 0.8), sr))
        feats.append(self.extract_features_fixed(self.shift(y), sr))
        feats.append(self.extract_features_fixed(self.pitch(y, sr, 0.7), sr))
        
        return np.stack(feats, axis=0)

    def segment_audio(self, audio_path, chunk_duration=6.0):
        """Segment the audio for analysis using energy-based and silence-based methods"""
        # Load audio
        y, sr = librosa.load(audio_path, sr=16000)
        
        # Energy-based coarse segmentation
        cs = int(chunk_duration * sr)
        chunks = []
        
        for i in range(0, len(y), cs):
            seg = y[i:i+cs]
            if len(seg) > sr * 0.5:  # At least 0.5 seconds
                energy = np.mean(seg**2)
                chunks.append({
                    'start': i/sr, 
                    'end': min((i+cs)/sr, len(y)/sr), 
                    'energy': energy,
                    'audio': seg
                })
        
        # Keep top 60% by energy
        chunks.sort(key=lambda x: x['energy'], reverse=True)
        keep = chunks[:int(len(chunks)*0.6)]
        keep.sort(key=lambda x: x['start'])
        
        return keep

    def classify_emotions(self, audio_segments):
        """Classify emotions based on the extracted audio features"""
        emotions = []
        confidences = []
        
        for segment in audio_segments:
            y = segment['audio']
            sr = 16000
            
            if len(y)/sr < 0.5:  # Skip very short segments
                continue
                
            # Extract features
            feats = self.get_features_from_wave(y, sr)
            X = self.scaler.transform(feats)[..., None]
            
            # Predict
            probs = self.model.predict(X, verbose=0)
            preds = np.argmax(probs, axis=1)
            lab_idx = np.bincount(preds).argmax()
            conf = float(np.max(np.mean(probs, axis=0)))
            
            # Get emotion label
            emotion = self.encoder.categories_[0][lab_idx]
            emotions.append(emotion)
            confidences.append(conf)
        
        return emotions, confidences

    def analyze(self, video_path):
        """Main analysis function"""
        # Extract audio from video
        audio_path = self.extract_audio(video_path)
        
        try:
            # Segment audio
            audio_segments = self.segment_audio(audio_path)
            
            # Classify emotions
            emotions, confidences = self.classify_emotions(audio_segments)
            
            # Aggregate results
            if emotions:
                emotion_counts = Counter(emotions)
                dominant_emotion = emotion_counts.most_common(1)[0][0]
                avg_confidence = np.mean(confidences)
                
                result = {
                    'dominant_emotion': dominant_emotion,
                    'avg_confidence': avg_confidence,
                    'emotion_distribution': dict(emotion_counts),
                    'total_segments': len(emotions),
                    'all_emotions': emotions,
                    'all_confidences': confidences
                }
            else:
                result = {
                    'dominant_emotion': 'unknown',
                    'avg_confidence': 0.0,
                    'emotion_distribution': {},
                    'total_segments': 0,
                    'all_emotions': [],
                    'all_confidences': []
                }
            
            return result
            
        finally:
            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)