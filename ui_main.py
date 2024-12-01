import ctypes
import os
import threading
import tkinter as tk
import json
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
from datetime import datetime
from datetime import datetime
from audio_handler import AudioRecorder, transcribe_audio
from predictor import predict_disease
from ui.styles.colors import COLORS

SESSIONS_DIR = "./data/sessions/"
SESSIONS_FILE = "./sessions.json"

class ChatSession:
    """Class to manage individual chat sessions"""
    def __init__(self, name):
        self.name = name
        self.messages = []

class DiseasesEaseApp:
    def __init__(self, root):
        # Initialize main window
        self.root = root
        self.root.title("DiseasesEaseAI")
        self.root.geometry("1200x800")
        self.root.configure(bg=COLORS['background'])

        # Add the icon to the window
        self.root.iconbitmap("./ui/assets/app-icon.ico")

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("DiseasesEaseAI")

        # Initialize sessions and recorder
        self.sessions = {}
        self.current_session = None
        self.recorder = AudioRecorder()
        self.is_recording = False  # Track recording status

        # Load microphone icon
        self.microphone_icon = self.load_icon("./ui/assets/mic-icon.png", (30, 30))

        # Setup UI
        self.setup_styles()
        self.create_layout()

        # Restore sessions from metadata, but do not create any default session
        self.restore_sessions()

    def restore_sessions(self):
        """Restore sessions from sessions.json on startup."""
        sessions = self.load_sessions()
        if not sessions:
            return  # Do not create any session automatically

        for session in sessions:
            session_name = session["name"]
            session_path = session["path"]

            # Restore session metadata and messages
            if not os.path.exists(session_path):
                continue  # Skip sessions with missing folders

            self.sessions[session_name] = ChatSession(session_name)
            transcription_path = os.path.join(session_path, "transcription1.txt")
            if os.path.exists(transcription_path):
                with open(transcription_path, "r") as f:
                    transcription = f.read()
                self.sessions[session_name].messages.append(f"{transcription}\n")
            self.sessions_list.insert(tk.END, session_name)

        # Disable buttons for the first session with data, if it exists
        if self.sessions_list.size() > 0:
            self.sessions_list.selection_set(0)
            self.on_session_select(None)

    def load_icon(self, path, size):
        """Load and resize an icon"""
        image = Image.open(path)
        image = image.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def setup_styles(self):
        """Configure custom styles for widgets."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure frame styles
        style.configure('Sidebar.TFrame', background=COLORS['sidebar'])

        # Configure button styles
        style.configure(
        'Primary.TButton',
        background=COLORS['primary'],
        foreground='white',
        font=('Segoe UI', 10),
        borderwidth=0,
        focuscolor='none'
        )
        style.map(
        'Primary.TButton',
        background=[('active', COLORS['primary_dark'])]
        )

        # Configure scrollbar styles
        style.configure('Vertical.TScrollbar', gripcount=0, background=COLORS['scrollbar'])

    def create_layout(self):
        """Create main application layout"""
        # Main container
        self.main_frame = ttk.Frame(self.root, style='Sidebar.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create sidebar
        self.create_sidebar()

        # Create chat area
        self.create_chat_area()

    def open_selected_session_folder(self):
        """Open the folder of the currently selected session (Windows only)."""
        try:
            selection = self.sessions_list.curselection()
            if selection:
                session_name = self.sessions_list.get(selection[0])
                session_path = os.path.abspath(os.path.join(SESSIONS_DIR, session_name))  # Get absolute path

                if os.path.exists(session_path):
                    self.open_session_folder(session_path)
                else:
                    self.notification_label.config(
                    text=f"Error: Folder for {session_name} does not exist. Path: {session_path}",
                    fg="red"
                    )
            else:
                self.notification_label.config(text="No session selected to open.", fg="red")
        except Exception as e:
            self.notification_label.config(text=f"Error opening folder: {e}", fg="red")
            print(f"Error opening session folder: {e}")

    def open_session_folder(self, session_path):
        """Open the session folder in the file explorer (Windows only)."""
        try:
            os.startfile(session_path)  # Windows-specific command to open folders/files
            self.notification_label.config(text=f"Opened folder: {session_path}", fg="#00FF00")
        except Exception as e:
            print(f"Error opening session folder: {e}")
            self.notification_label.config(text=f"Error opening folder: {e}", fg="red")

    def create_sidebar(self):
        """Create sidebar with session management."""
        sidebar = ttk.Frame(self.main_frame, style='Sidebar.TFrame')
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        header = ttk.Label(
        sidebar, text="Chat Sessions",
        font=('Segoe UI', 16, 'bold'),
        foreground=COLORS['text'], background=COLORS['header_bg']
        )
        header.pack(fill=tk.X, pady=(0, 20))

        # New Session button
        self.create_rounded_button(sidebar, text="New Session", command=self.create_new_session).pack(fill=tk.X, pady=(0, 10))

        # Sessions list
        self.sessions_list_frame = ttk.Frame(sidebar)
        self.sessions_list_frame.pack(fill=tk.BOTH, expand=True)

        self.sessions_list = tk.Listbox(
        self.sessions_list_frame, bg=COLORS['sidebar'], fg=COLORS['text'], selectmode=tk.SINGLE,
        font=('Segoe UI', 11), relief=tk.FLAT, width=25, height=20,
        selectbackground=COLORS['primary'], selectforeground='white'
        )
        self.sessions_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.sessions_list.bind('<<ListboxSelect>>', self.on_session_select)

        # Scrollbar
        self.sidebar_scrollbar = ttk.Scrollbar(
        self.sessions_list_frame, orient=tk.VERTICAL, command=self.sessions_list.yview
        )
        self.sidebar_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sessions_list.config(yscrollcommand=self.sidebar_scrollbar.set)

        # Delete Session button
        self.delete_button = tk.Button(
        sidebar, text="Delete Session", command=self.delete_selected_session,
        bg=COLORS['primary'], fg='white', font=('Segoe UI', 10), relief=tk.FLAT
        )
        self.delete_button.pack(fill=tk.X, pady=(10, 0))

        # Clear All Sessions button
        self.clear_all_button = tk.Button(
        sidebar, text="Clear All Sessions", command=self.clear_all_sessions,
        bg=COLORS['primary_dark'], fg='white', font=('Segoe UI', 10), relief=tk.FLAT
        )
        self.clear_all_button.pack(fill=tk.X, pady=(10, 0))

        # Open Session Folder button
        self.open_folder_button = tk.Button(
        sidebar, text="Open Session Folder", command=self.open_selected_session_folder,
        bg=COLORS['primary_dark'], fg='white', font=('Segoe UI', 10), relief=tk.FLAT
        )
        self.open_folder_button.pack(fill=tk.X, pady=(10, 0))

    def create_chat_area(self):
        """Create main chat display and input area."""
        chat_frame = ttk.Frame(self.main_frame, style='Sidebar.TFrame')
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Notification Label (initialize early)
        self.notification_label = tk.Label(
        chat_frame, text="Welcome to DiseasesEaseAI!",
        font=('Segoe UI', 12), bg=COLORS['background'],
        fg="#00FF00", anchor="w"
        )
        self.notification_label.pack(fill=tk.X, pady=(0, 10))  # Positioned at the top of the chat area

        # Chat Display Area
        self.chat_display = ScrolledText(
        chat_frame, wrap=tk.WORD, font=('Segoe UI', 11),
        bg=COLORS['background'], fg=COLORS['text'], relief=tk.FLAT
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=(0, 10), pady=(0, 10))

        # Buttons Area at the bottom-right
        buttons_frame = ttk.Frame(chat_frame, style='Sidebar.TFrame')
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10, anchor="e")

        # Open Session Folder Button
        self.open_folder_button = ttk.Button(
        buttons_frame, text="Open Session Folder", command=self.open_selected_session_folder,
        style="Primary.TButton"
        )
        self.open_folder_button.pack(side=tk.RIGHT, padx=(5, 0), pady=5)

        # Record Button
        self.record_button = ttk.Button(
        buttons_frame, text="Record", command=self.toggle_recording, style="Primary.TButton"
        )
        self.record_button.pack(side=tk.RIGHT, padx=(5, 5), pady=5)

        # Analyze Button
        self.analyze_button = ttk.Button(
        buttons_frame, text="Analyze", command=self.analyze, style="Primary.TButton"
        )
        self.analyze_button.pack(side=tk.RIGHT, padx=(0, 5), pady=5)

    def create_circular_button(self, parent, image, command=None, diameter=40):
        """Create a circular button using Canvas"""
        canvas = tk.Canvas(parent, width=diameter, height=diameter, bg=COLORS['sidebar'], highlightthickness=0)
        canvas.pack_propagate(False)
        circle = canvas.create_oval(2, 2, diameter-2, diameter-2, fill=COLORS['primary'], outline=COLORS['primary'])
        button = tk.Button(
            canvas, image=image, command=command,
            bg=COLORS['primary'], relief=tk.FLAT, highlightthickness=0
        )
        button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        return canvas

    def create_rounded_button(self, parent, text, command=None, width=10):
        """Create a rounded button using Canvas"""
        canvas = tk.Canvas(parent, width=width*10, height=40, bg=COLORS['sidebar'], highlightthickness=0)
        canvas.pack_propagate(False)
        rect = canvas.create_oval(5, 5, width*10-5, 35, fill=COLORS['primary'], outline=COLORS['primary'])
        button = tk.Button(
            canvas, text=text, command=command,
            font=('Segoe UI', 10), bg=COLORS['primary'], fg='white',
            relief=tk.FLAT, highlightthickness=0
        )
        button.pack(fill=tk.BOTH, expand=True)
        return canvas

    def create_new_session(self):
        """Create a new session folder and add it to the session list."""
        try:
            if not os.path.exists(SESSIONS_DIR):
                os.makedirs(SESSIONS_DIR)

            # Load existing sessions
            sessions = self.load_sessions() if isinstance(self.load_sessions(), list) else []

            # Determine the next session index
            new_index = len(sessions) + 1
            session_name = f"Session_{new_index}"
            session_path = os.path.join(SESSIONS_DIR, session_name)

            # Create the session folder
            os.makedirs(session_path, exist_ok=True)

            # Add session metadata
            sessions.append({
                "name": session_name,
                "path": session_path,
                "created_at": datetime.now().isoformat()
            })
            self.save_sessions(sessions)

            # Update the UI
            self.sessions[session_name] = ChatSession(session_name)
            self.sessions_list.insert(tk.END, session_name)
            self.current_session = session_name
            self.clear_chat_display()

            # Enable buttons for the new session
            self.record_button.config(state=tk.NORMAL)
            self.analyze_button.config(state=tk.NORMAL)

            self.notification_label.config(text=f"New session {session_name} created.", fg="#00FF00")
        except Exception as e:
            self.notification_label.config(text=f"Error creating session: {e}", fg="red")
            print(f"Error during create_new_session: {e}")

    def on_session_select(self, event):
        """Handle session selection."""
        try:
            selection = self.sessions_list.curselection()
            if selection:
                # Get the selected session name
                session_name = self.sessions_list.get(selection[0])
                self.current_session = session_name
                self.notification_label.config(text=f"Session {session_name} selected.", fg="#00FF00")

                # Load the session's content
                session_path = self.get_current_session_path()
                if not os.path.exists(session_path):
                    self.notification_label.config(text=f"Error: Session {session_name} folder is missing.", fg="red")
                    return

                # Clear chat display
                self.clear_chat_display()

                # Load all transcription and analysis files
                transcription_files = [
                    f for f in os.listdir(session_path) if f.startswith("transcription") and f.endswith(".txt")
                ]
                transcription_files.sort()  # Ensure files are loaded in order

                # Display content in the chat
                for transcription_file in transcription_files:
                    transcription_path = os.path.join(session_path, transcription_file)
                    with open(transcription_path, "r") as f:
                        content = f.read()
                    self.chat_display.insert(tk.END, f"Content of {transcription_file}:\n{content}\n")
                    self.chat_display.insert(tk.END, "-" * 50 + "\n")

                # Check if the session is already analyzed
                existing_audio = [
                    f for f in os.listdir(session_path) if f.startswith("output") and f.endswith(".wav")
                ]
                if transcription_files or existing_audio:
                    # Disable Record and Analyze buttons
                    self.record_button.config(state=tk.DISABLED)
                    self.analyze_button.config(state=tk.DISABLED)

                    # Update the notification label
                    self.notification_label.config(
                        text="This is an analyzed session. You can view it without editing.", 
                        fg="orange"
                    )
                else:
                    # Enable buttons for a fresh session
                    self.record_button.config(state=tk.NORMAL)
                    self.analyze_button.config(state=tk.NORMAL)
        except Exception as e:
            self.notification_label.config(text=f"Error: {e}", fg="red")
            print(f"Error during on_session_select: {e}")

    def load_sessions(self):
        """Load session metadata from sessions.json."""
        if os.path.exists(SESSIONS_FILE): 
            try:
                with open(SESSIONS_FILE, "r") as f: # write to json
                    return json.load(f)
            except json.JSONDecodeError:
                print("Error: Corrupted sessions.json. Recreating.")
                return []
        return []

    def save_sessions(self, sessions):
        """Save session metadata to sessions.json."""
        with open(SESSIONS_FILE, "w") as f: # Read from json
            json.dump(sessions, f, indent=4)

    def load_session_messages(self, session_name):
        """Load messages for the selected session."""
        self.clear_chat_display()
        if session_name in self.sessions:
            for message in self.sessions[session_name].messages:
                self.chat_display.insert(tk.END, message)

    def toggle_recording(self):
        """Toggle between starting and stopping recording."""
        try:
            if not self.is_recording:
                # Ensure a valid session exists
                if not self.current_session or not os.path.exists(self.get_current_session_path()):
                    self.create_new_session()

                # Start recording
                self.start_recording()
            else:
                # Stop recording
                self.stop_recording()
        except Exception as e:
            self.notification_label.config(text=f"Error: {e}", fg="red")
            print(f"Error during toggle_recording: {e}")

    def start_recording(self):
        """Start audio recording."""
        try:
            session_path = self.get_current_session_path()
            if not os.path.exists(session_path):
                os.makedirs(session_path)

            # Determine filenames for the new recording
            existing_transcripts = [
                f for f in os.listdir(session_path) if f.startswith("transcription") and f.endswith(".txt")
            ]
            new_file_index = len(existing_transcripts) + 1

            # Set filenames for the new recording
            self.recorder.filename = os.path.join(session_path, f"output{new_file_index}.wav")
            self.transcription_file = os.path.join(session_path, f"transcription{new_file_index}.txt")

            self.recorder.start_recording()
            self.is_recording = True
            threading.Thread(target=self.recorder.record, daemon=True).start()
            self.notification_label.config(text="Recording started...", fg="#00FF00")
        except Exception as e:
            self.notification_label.config(text=f"Error: {e}", fg="red")
            print(f"Error during start_recording: {e}")

    def stop_recording(self):
        """Stop audio recording and save transcription."""
        try:
            if not self.current_session:
                self.notification_label.config(text="No active session. Cannot stop recording.", fg="red")
                return

            self.recorder.stop_recording()
            self.is_recording = False

            # Transcribe the audio
            transcription = transcribe_audio(self.recorder.filename)
            session_path = self.get_current_session_path()

            # Save transcription
            transcription_files = [
                f for f in os.listdir(session_path) if f.startswith("transcription") and f.endswith(".txt")
            ]
            new_file_index = len(transcription_files) + 1
            transcription_path = os.path.join(session_path, f"transcription{new_file_index}.txt")
            with open(transcription_path, "w") as f:
                f.write(transcription)

            # Display the transcription in the chat
            self.chat_display.insert(tk.END, f"Transcription:\n{transcription}\n")
            self.notification_label.config(text="Recording stopped. Transcription saved.", fg="#00FF00")
        except Exception as e:
            self.notification_label.config(text=f"Error: {e}", fg="red")
            print(f"Error stopping recording: {e}")

    def get_current_session_path(self):
        """Get the folder path of the current session."""
        if not self.current_session:
            raise ValueError("No session is currently active.")

        session_path = os.path.join(SESSIONS_DIR, self.current_session)
        if not os.path.exists(session_path):
            # Automatically create the session folder if it was deleted
            os.makedirs(session_path, exist_ok=True)
            self.notification_label.config(text=f"Recreated session folder: {self.current_session}", fg="#00FF00")
        return session_path

    def analyze(self):
        """Analyze the transcription and predict diseases."""
        try:
            # Check if a session is active
            if not self.current_session:
                self.notification_label.config(text="No active session for analysis.", fg="red")
                return

            # Check if the transcription file exists
            session_path = self.get_current_session_path()
            transcription_files = [
                f for f in os.listdir(session_path) if f.startswith("transcription") and f.endswith(".txt")
            ]
            if not transcription_files:
                self.notification_label.config(text="No transcription file found for analysis.", fg="red")
                return

            # Use the latest transcription file
            transcription_file = os.path.join(session_path, sorted(transcription_files)[-1])
            with open(transcription_file, "r") as f:
                transcription = f.read().strip()

            if not transcription:
                self.notification_label.config(text="Transcription is empty. Cannot analyze.", fg="red")
                return

            # Perform analysis
            predictions = predict_disease(transcription)
            result = "\n".join([f"{disease}: {prob:.2%}" for disease, prob in predictions])
        
            # Append the analysis result to the transcription file
            with open(transcription_file, "a") as f:
                f.write(f"\n\nAnalysis Result:\n{result}")

            # Display the transcription and analysis in the chat
            self.chat_display.insert(tk.END, f"\nAnalysis Result:\n{result}\n")
            self.notification_label.config(text="Analysis successful.", fg="#00FF00")

            # Disable recording and analyzing for this session
            self.record_button.config(state=tk.DISABLED)
            self.analyze_button.config(state=tk.DISABLED)

        except Exception as e:
            self.notification_label.config(text=f"Error: {e}", fg="red")
            print(f"Error during analysis: {e}")

    def create_sidebar(self):
        """Create sidebar with session management."""
        sidebar = ttk.Frame(self.main_frame, style='Sidebar.TFrame')
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        header = ttk.Label(
        sidebar, text="Chat Sessions",
        font=('Segoe UI', 16, 'bold'),
        foreground=COLORS['text'], background=COLORS['header_bg']
        )
        header.pack(fill=tk.X, pady=(0, 20))

        # New Session button
        self.create_rounded_button(sidebar, text="New Session", command=self.create_new_session).pack(fill=tk.X, pady=(0, 10))

        # Sessions list
        self.sessions_list_frame = ttk.Frame(sidebar)
        self.sessions_list_frame.pack(fill=tk.BOTH, expand=True)

        self.sessions_list = tk.Listbox(
        self.sessions_list_frame, bg=COLORS['sidebar'], fg=COLORS['text'], selectmode=tk.SINGLE,
        font=('Segoe UI', 11), relief=tk.FLAT, width=25, height=20,
        selectbackground=COLORS['primary'], selectforeground='white'
        )
        self.sessions_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.sessions_list.bind('<<ListboxSelect>>', self.on_session_select)

        # Scrollbar
        self.sidebar_scrollbar = ttk.Scrollbar(
        self.sessions_list_frame, orient=tk.VERTICAL, command=self.sessions_list.yview
        )
        self.sidebar_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sessions_list.config(yscrollcommand=self.sidebar_scrollbar.set)

        # Delete Session button
        self.delete_button = tk.Button(
        sidebar, text="Delete Session", command=self.delete_selected_session,
        bg=COLORS['primary'], fg='white', font=('Segoe UI', 10), relief=tk.FLAT
        )
        self.delete_button.pack(fill=tk.X, pady=(10, 0))

        # Clear All Sessions button
        self.clear_all_button = tk.Button(
        sidebar, text="Clear All Sessions", command=self.clear_all_sessions,
        bg=COLORS['primary_dark'], fg='white', font=('Segoe UI', 10), relief=tk.FLAT
        )
        self.clear_all_button.pack(fill=tk.X, pady=(10, 0))

    def delete_selected_session(self):
        """Delete the currently selected session and its data."""
        selection = self.sessions_list.curselection()
        if selection:
            session_name = self.sessions_list.get(selection[0])
            session_path = os.path.join(SESSIONS_DIR, session_name)

            # Delete the session folder
            if os.path.exists(session_path):
                import shutil
                shutil.rmtree(session_path)

            # Remove session from memory and UI
            del self.sessions[session_name]
            self.sessions_list.delete(selection[0])

            # Reset current session if it matches the deleted session
            if self.current_session == session_name:
                self.current_session = None
                self.clear_chat_display()
                self.notification_label.config(text=f"Session {session_name} deleted.", fg="#FF4500")

            # Update the sessions.json file
            self.save_sessions([
                {"name": name, "path": os.path.join(SESSIONS_DIR, name)}
                for name in self.sessions
            ])
        else:
            self.notification_label.config(text="No session selected to delete.", fg="red")

    def clear_all_sessions(self):
        """Clear all sessions from UI and filesystem."""
        import shutil
        if os.path.exists(SESSIONS_DIR):
            shutil.rmtree(SESSIONS_DIR)
        os.makedirs(SESSIONS_DIR)
        self.sessions.clear()
        self.sessions_list.delete(0, tk.END)
        self.save_sessions([])
        self.notification_label.config(text="All sessions cleared.", fg="#FF4500")

    def clear_chat_display(self):
        """Clear the chat display area."""
        self.chat_display.delete('1.0', tk.END)

def main():
    """Initialize and run the application"""
    root = tk.Tk()
    app = DiseasesEaseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()