DiseasesEaseAI
DiseasesEaseAI is an AI-powered application designed to assist healthcare providers by automating the analysis of audio consultations. The system supports recording, transcription, and disease prediction using a simple and intuitive graphical user interface (GUI).

Features
Audio Recording: Record consultations directly in the app.
Speech-to-Text: Convert audio recordings to text using transcription.
Disease Prediction: Analyze transcripts for potential diseases with probabilities.
Session Management: Manage multiple chat sessions with storage and retrieval.
Dark Mode: Modern and visually appealing UI with dark mode colors.
Customizable Styles: Store UI styles (e.g., colors) in external files for easy customization.

Supported Diseases
SymptomEaseAI currently predicts the following 7 diseases based on the recorded symptoms:

        1: 'Upper Respiratory Tract Infection',
        2: 'Dermatitis',
        3: 'Gastritis',
        4: 'Rhinitis',
        5: 'Viral Hepatitis',
        6: 'Enteritis',
        7: 'Pneumonia'

Installation
Prerequisites
Python 3.7 or higher
Required Python packages: Pillow, tkinter, threading, datetime, and any AI/ML packages for transcription and prediction.
Tools for packaging as .exe: pyinstaller

Steps
1. Clone this repository: 
git clone https://github.com/SymptomsEaseAi.git
cd DiseasesEaseAI

2. Install dependencies:
pip install -r requirements.txt

3. Run the app:
python ui_main.py


File Structure 
DiseasesEaseAI/
├── audio_handler.py    # Handles audio recording and transcription
├── predictor.py        # Handles disease prediction
├── ui_main.py          # Main user interface (entry point)
├── models/             # AI models and Vosk model storage
│   ├── trained_model.h5
│   ├── features.pkl
│   ├── scaler.pkl
│   ├── vosk-model/
├── data/               # Temporary storage for audio and transcriptions
│   ├── session_audio/
│   │   ├── session_1_audio.wav
│   │   └── session_2_audio.wav
│   ├── session_transcriptions/
│       ├── session_1_transcription.txt
│       └── session_2_transcription.txt
|---Docs/
├── requirements.txt    # Dependency list for seamless installation
├── README.md           # Documentation
└── tests/              # Unit and integration tests


# Usage
Start the Application: Run ui_main.py to launch the DiseasesEaseAI interface.

Create a New Session:

Click "New Session" in the sidebar.
Enter session details as prompted.
Record Audio:

Click the "Record" button to start recording.
Click "Stop" to save the audio file.
Analyze Audio:

Click the "Analyze" button after recording to transcribe and predict diseases.
View Results:

The transcription and predictions will appear in the chat area.
The session data is saved for future access.
Manage Sessions:

Use the sidebar to switch between sessions, delete sessions, or clear all sessions.

Technical Details
Core Components
GUI:

Built with tkinter for simplicity and portability.
UI components styled using Pillow for icons and external JSON for colors.
Audio Handling:

audio_handler.py manages audio recording and transcription using custom libraries or external APIs.
AI Prediction:

predictor.py analyzes the transcriptions using a trained machine learning model.
Session Management:

Session data (audio, transcriptions, predictions) is stored in the data/sessions/ directory.
Metadata is saved in sessions.json.
Custom Styles:

UI colors are defined in ./ui/styles/colors.json for easy modification.

Technical Requirements
System Requirements
Operating System:
Windows 10 or higher
Processor: Intel i5 or equivalent (minimum), i7 or equivalent (recommended)
RAM:
Minimum: 4 GB
Recommended: 8 GB or higher
Disk Space: At least 500 MB free for application files and dependencies
Audio Hardware: A functional microphone for recording consultations.


5. FAQs and Troubleshooting
Q: Why is the app not recording audio?
Ensure your microphone is connected and permissions are granted.
Check your system's audio input settings.
Q: How do I update the application's UI colors?
Open ./ui/styles/colors.json in a text editor.
Modify the JSON values (e.g., background, primary).
Restart the application to apply changes.
Q: How do I update the AI model for disease prediction?
Replace the predictor module or AI model file with the new version.
Ensure compatibility with the current application.
Q: What if the transcription is inaccurate?
Check your microphone quality and reduce background noise.
Consider using an advanced speech-to-text library or API.
Q: How do I recover a deleted session?
Sessions cannot be recovered once deleted. Ensure to back up important data.

6. Contact Information
If you encounter any issues or need assistance, contact:

Support Email: ferasalkhodari51@gmail.com
Documentation and Updates: SymptomsEaseAi.github
