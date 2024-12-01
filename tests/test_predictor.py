import pytest
from predictor import predict_disease

def test_predict_disease_valid():
    # Test disease prediction with valid transcription
    transcription = "respiratory infection dermatitis"  # Example symptoms related to diseases
    predictions = predict_disease(transcription)
    assert len(predictions) == 2  # Ensure the top-2 predictions are returned
    for disease, probability in predictions:
        assert isinstance(disease, str)  # Disease name should be a string
        assert disease in [
            'Upper Respiratory Tract Infection',
            'Dermatitis',
            'Gastritis',
            'Rhinitis',
            'Viral Hepatitis',
            'Enteritis',
            'Pneumonia'
        ]  # Validate the disease is one of the known diseases
        assert 0 <= probability <= 1  # Probability should be between 0 and 1

def test_predict_disease_empty():
    # Test disease prediction with empty transcription
    transcription = ""
    predictions = predict_disease(transcription)
    assert len(predictions) == 2  # Ensure the top-2 predictions are returned
    for disease, probability in predictions:
        assert disease in [
            'Upper Respiratory Tract Infection',
            'Dermatitis',
            'Gastritis',
            'Rhinitis',
            'Viral Hepatitis',
            'Enteritis',
            'Pneumonia'
        ]  # Validate the disease is one of the known diseases
        assert 0 <= probability <= 1  # Ensure probabilities are within the valid range
