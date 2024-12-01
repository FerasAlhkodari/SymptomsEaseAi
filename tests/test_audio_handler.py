import os
import pytest
from audio_handler import AudioRecorder, transcribe_audio

def test_start_stop_recording():
    """Test starting and stopping audio recording."""
    test_filename = "test_output.wav"
    recorder = AudioRecorder(filename=test_filename)
    
    recorder.start_recording()
    assert recorder.is_recording is True
    
    recorder.stop_recording()
    assert recorder.is_recording is False
    assert os.path.exists(test_filename)
    os.remove(test_filename)  # Clean up

def test_transcribe_audio_invalid_file():
    """Test transcription with a nonexistent audio file."""
    invalid_filename = "nonexistent_audio.wav"
    with pytest.raises(FileNotFoundError):
        transcribe_audio(invalid_filename)
