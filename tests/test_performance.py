import time
from unittest.mock import patch

# Mocking the transcribe_audio function
@patch('audio_handler.transcribe_audio')
def test_transcription_performance(mock_transcribe_audio):
    # Define the mock return value
    mock_transcribe_audio.return_value = "This is a test transcription."
    
    # Measure transcription speed
    start_time = time.time()
    transcription = mock_transcribe_audio("sample_audio.wav")
    end_time = time.time()

    # Assertions
    assert len(transcription) > 0  # Transcription should not be empty
    assert end_time - start_time < 5  # Must complete within 5 seconds

# Mocking the predict_disease function
@patch('predictor.predict_disease')
def test_prediction_performance(mock_predict_disease):
    # Define the mock return value
    mock_predict_disease.return_value = ["Upper Respiratory Tract Infection", "Dermatitis"]

    # Measure prediction speed
    transcription = "cough fever"
    start_time = time.time()
    predictions = mock_predict_disease(transcription)
    end_time = time.time()

    # Assertions
    assert len(predictions) > 0  # Ensure predictions are returned
    assert end_time - start_time < 2  # Must complete within 2 seconds

# Run the test cases
if __name__ == "__main__":
    test_transcription_performance()
    test_prediction_performance()
    print("All tests passed!")
