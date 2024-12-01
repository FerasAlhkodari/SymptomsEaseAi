from unittest.mock import patch
from ui_main import DiseasesEaseApp
from tkinter import Tk

def test_create_new_session():
    # Test session creation
    root = Tk()
    app = DiseasesEaseApp(root)
    # Get the initial count of sessions
    initial_session_count = len(app.sessions)
    # Create a new session
    app.create_new_session()
    # Ensure one additional session is created
    assert len(app.sessions) == initial_session_count + 1  
    # Validate the naming convention of the newly created session
    session_name = list(app.sessions.keys())[-1]  # Get the latest session name
    assert session_name.startswith("Session_")  
    root.destroy()


@patch("ui_main.DiseasesEaseApp.get_current_session_path")
def test_toggle_recording(mock_get_path):
    # Test toggling recording functionality
    root = Tk()
    app = DiseasesEaseApp(root)
    mock_get_path.return_value = "./data/session_audio/Session_1"
    app.create_new_session()
    app.toggle_recording()
    assert app.is_recording is True  # Verify recording is active
    app.toggle_recording()
    assert app.is_recording is False  # Verify recording is stopped
    root.destroy()
