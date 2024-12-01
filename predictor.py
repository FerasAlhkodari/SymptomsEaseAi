import numpy as np
import pickle
from tensorflow.keras.models import load_model

# Load model and preprocessing tools
model = load_model('./models/trained_model.h5')
with open('./models/features.pkl', 'rb') as f:
    features = pickle.load(f)
with open('./models/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

def predict_disease(transcription):
    def dialog_to_count_vector(dialog, features):
        vector = np.zeros(len(features))
        tokens = dialog.lower().split()
        for token in tokens:
            if token in features:
                index = features.index(token)
                vector[index] += 1
        return vector

    vector = dialog_to_count_vector(transcription, features)
    vector_scaled = scaler.transform([vector])
    probabilities = model.predict(vector_scaled)[0]
    disease_dict = {
        1: 'Upper Respiratory Tract Infection',
        2: 'Dermatitis',
        3: 'Gastritis',
        4: 'Rhinitis',
        5: 'Viral Hepatitis',
        6: 'Enteritis',
        7: 'Pneumonia'
    }
    top_indices = np.argsort(probabilities)[-2:][::-1]
    predictions = [(disease_dict.get(i + 1, "Unknown"), probabilities[i]) for i in top_indices]
    return predictions
