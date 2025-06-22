from tensorflow.keras.models import load_model
import numpy as np

class EmotionModel:
    def __init__(self, model_path):
        self.model = load_model(model_path)
        self.emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

    def preprocess_input(self, audio_features):
        # Normalize the input features
        audio_features = np.array(audio_features)
        audio_features = (audio_features - np.mean(audio_features)) / np.std(audio_features)
        return audio_features.reshape(1, -1)

    def predict_emotion(self, audio_features):
        processed_features = self.preprocess_input(audio_features)
        prediction = self.model.predict(processed_features)
        emotion_index = np.argmax(prediction)
        return self.emotion_labels[emotion_index]