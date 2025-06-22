# In your emotion analyzer or in a separate script
import pickle

# Load the encoder
with open('video-interview-system\models\encoder.pkl', 'rb') as f:
    encoder = pickle.load(f)

# Print available emotion classes
print("Available emotion classes:", encoder.categories_[0])