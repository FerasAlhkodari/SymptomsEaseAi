import pytest
from unittest.mock import patch
from predictor import predict_disease

def test_transcription_prediction_integration():
    # Simulated transcription output
    simulated_transcription = "Patient reports fever and sore throat."

    # Mock the transcribe_audio function
    with patch('audio_handler.transcribe_audio', return_value=simulated_transcription):
        # Test the workflow: transcription followed by prediction
        transcription = simulated_transcription  # Mocked transcription
        predictions = predict_disease(transcription)

        assert predictions is not None  # Predictions should not be None
        assert len(predictions) > 0  # Ensure predictions are returned

        for disease, probability in predictions:
            assert isinstance(disease, str)  # Validate disease name
            assert 0 <= probability <= 1  # Validate probability range
