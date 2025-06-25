import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
import threading
from transcribe import transcribe_audio_file
import os
import queue

class TranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Transcription")
        self.root.geometry("600x500")
        
        # Create and configure grid
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # File selection frame
        self.file_frame = ttk.Frame(root, padding="10")
        self.file_frame.grid(row=0, column=0, sticky="ew")
        
        self.file_path = tk.StringVar()
        self.file_label = ttk.Label(self.file_frame, textvariable=self.file_path, wraplength=500)
        self.file_label.grid(row=0, column=0, sticky="ew", padx=5)
        
        self.select_button = ttk.Button(self.file_frame, text="Select M4A File", command=self.select_file)
        self.select_button.grid(row=0, column=1, padx=5)
        
        # Progress frame
        self.progress_frame = ttk.Frame(root, padding="10")
        self.progress_frame.grid(row=1, column=0, sticky="ew")
        
        self.progress = ttk.Progressbar(self.progress_frame, length=400, mode='determinate')
        self.progress.grid(row=0, column=0, sticky="ew")
        
        self.progress_label = ttk.Label(self.progress_frame, text="0%")
        self.progress_label.grid(row=0, column=1, padx=5)
        
        # Transcription text area
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, padx=10, pady=10)
        self.text_area.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        # Start button
        self.start_button = ttk.Button(root, text="Start Transcription", command=self.start_transcription, state="disabled")
        self.start_button.grid(row=3, column=0, pady=10)
        
        # Progress queue for communication between threads
        self.progress_queue = queue.Queue()
        
        # Configure grid weights
        self.file_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_columnconfigure(0, weight=1)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("M4A files", "*.m4a")],
            title="Select an M4A file"
        )
        if file_path:
            self.file_path.set(file_path)
            self.start_button.config(state="normal")
            self.text_area.delete(1.0, tk.END)
            self.progress['value'] = 0
            self.progress_label['text'] = "0%"

    def update_progress(self, progress):
        self.progress['value'] = progress
        self.progress_label['text'] = f"{progress:.1f}%"
        self.root.update_idletasks()

    def check_progress_queue(self):
        try:
            while True:
                msg = self.progress_queue.get_nowait()
                if isinstance(msg, float):  # Progress update
                    self.update_progress(msg)
                elif isinstance(msg, str):  # Final transcription
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, msg)
                    self.start_button.config(state="normal")
                    return
        except queue.Empty:
            self.root.after(100, self.check_progress_queue)

    def transcribe_with_progress(self):
        input_path = self.file_path.get()
        output_path = "transcription.txt"
        
        def progress_callback(progress):
            self.progress_queue.put(progress)
        
        # Start transcription
        transcribe_audio_file(input_path, output_path, progress_callback)
        
        # Read the transcription file and show it
        try:
            with open(output_path, 'r') as f:
                transcription = f.read()
            self.progress_queue.put(transcription)
        except Exception as e:
            self.progress_queue.put(f"Error reading transcription: {str(e)}")

    def start_transcription(self):
        self.start_button.config(state="disabled")
        self.progress['value'] = 0
        self.progress_label['text'] = "0%"
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "Transcribing... Please wait...")
        
        # Start transcription in a separate thread
        thread = threading.Thread(target=self.transcribe_with_progress)
        thread.daemon = True
        thread.start()
        
        # Start checking for progress updates
        self.check_progress_queue()

if __name__ == "__main__":
    root = tk.Tk()
    app = TranscriptionApp(root)
    root.mainloop()
