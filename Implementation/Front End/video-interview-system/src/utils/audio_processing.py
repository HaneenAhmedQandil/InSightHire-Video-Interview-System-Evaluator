def extract_features(audio_file):
    # Function to extract features from audio file
    import librosa
    import numpy as np

    # Load audio file
    y, sr = librosa.load(audio_file, sr=None)
    
    # Extract features (e.g., MFCCs)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return np.mean(mfccs.T, axis=0)

def add_noise(audio_file, noise_factor=0.005):
    # Function to add noise to an audio file
    import numpy as np
    import librosa

    # Load audio file
    y, sr = librosa.load(audio_file, sr=None)
    
    # Generate random noise
    noise = np.random.randn(len(y))
    
    # Add noise to the audio signal
    noisy_audio = y + noise_factor * noise
    return noisy_audio, sr

def save_audio(audio_data, sr, output_file):
    # Function to save audio data to a file
    import soundfile as sf

    sf.write(output_file, audio_data, sr)