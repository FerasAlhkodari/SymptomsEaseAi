import os
import wave
import json
import threading
from vosk import Model, KaldiRecognizer
import pyaudio


class AudioRecorder:
    def __init__(self, device_index=0, filename="output.wav"):
        """Initialize the AudioRecorder."""
        self.device_index = device_index
        self.filename = filename
        self.chunk = 1024  # Buffer size
        self.format = pyaudio.paInt16  # 16-bit audio format
        self.channels = 1  # Mono audio
        self.rate = 16000  # Vosk requires 16 kHz
        self.frames = []  # Stores audio frames
        self.is_recording = False  # Tracks if recording is active

    def start_recording(self):
        """Start audio recording."""
        try:
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk
            )
            self.is_recording = True
            self.frames = []
            print(f"Recording started: {self.filename}")
        except Exception as e:
            print(f"Error starting recording: {e}")
            raise

    def stop_recording(self):
        """Stop audio recording and save to file."""
        try:
            if not self.is_recording:
                print("Recording is not active.")
                return

            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

            # Save the recorded audio to a .wav file
            with wave.open(self.filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.p.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.frames))
            print(f"Recording stopped and saved to {self.filename}")
        except Exception as e:
            print(f"Error stopping recording: {e}")
            raise

    def record(self):
        """Capture audio data while recording."""
        try:
            while self.is_recording:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
        except Exception as e:
            print(f"Error during recording: {e}")
            self.is_recording = False


def transcribe_audio(audio_file="output.wav"):
    """Transcribe the given audio file using the Vosk model."""
    model_path = "./models/vosk-model-small-en-us-0.15"

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")

    try:
        # Load the Vosk model
        model = Model(model_path)
        print("Vosk model loaded successfully.")

        # Open the audio file
        with wave.open(audio_file, "rb") as wf:
            print(f"Processing audio file: {audio_file}")
            if wf.getnchannels() != 1:
                raise ValueError("Audio file must be mono (1 channel)")
            if wf.getsampwidth() != 2:
                raise ValueError("Audio file must have 16-bit samples")
            if wf.getframerate() != 16000:
                raise ValueError("Audio file must have a sample rate of 16000 Hz")

            recognizer = KaldiRecognizer(model, wf.getframerate())
            transcription = []

            # Process the audio frames
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    transcription.append(result.get("text", ""))

            # Get the final result
            final_result = json.loads(recognizer.FinalResult())
            transcription.append(final_result.get("text", ""))
            print(f"Final result: {final_result}")

            final_transcription = " ".join(transcription)
            print(f"Final transcription: {final_transcription}")
            return final_transcription

    except FileNotFoundError as fnfe:
        print(f"File not found: {fnfe}")
        raise
    except Exception as e:
        print(f"Error during transcription: {e}")
        raise
