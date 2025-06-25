import os
import sys
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import argparse
import json
import multiprocessing as mp
from multiprocessing import Manager, Lock
import time

def load_progress(progress_file):
    """Load progress from file"""
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {'last_chunk': -1, 'transcribed_text': {}}
    return {'last_chunk': -1, 'transcribed_text': {}}

def save_progress(progress_file, chunk_index, text, lock):
    """Save progress to file with lock"""
    with lock:
        try:
            # Initialize progress structure
            progress = {'last_chunk': -1, 'transcribed_text': {}}
            
            # Load existing progress if file exists
            if os.path.exists(progress_file):
                try:
                    with open(progress_file, 'r') as f:
                        progress = json.load(f)
                except json.JSONDecodeError:
                    pass
            
            # Ensure transcribed_text is a dictionary
            if not isinstance(progress['transcribed_text'], dict):
                progress['transcribed_text'] = {}
            
            # Update progress
            progress['transcribed_text'][str(chunk_index)] = text
            progress['last_chunk'] = max(progress['last_chunk'], chunk_index)
            
            # Save updated progress
            with open(progress_file, 'w') as f:
                json.dump(progress, f)
        except Exception as e:
            print(f"Error saving progress: {e}")

def process_chunk(chunk_data):
    """Process a single chunk in a worker process"""
    chunk, chunk_index, total_chunks, progress_file, lock, progress_callback = chunk_data
    
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    # Export chunk as temporary file with unique process ID
    chunk_filename = f"temp_chunk_{chunk_index}_{os.getpid()}.wav"
    chunk.export(chunk_filename, format="wav")
    
    try:
        # Recognize chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language="en-US")
                progress = (chunk_index + 1) / total_chunks * 100
                if progress_callback:
                    progress_callback(progress)
                else:
                    print(f"Progress: {progress:.1f}% (Chunk {chunk_index+1}/{total_chunks} transcribed)")
                # Save progress
                save_progress(progress_file, chunk_index, text, lock)
                return chunk_index, text
            except sr.UnknownValueError:
                print(f"Chunk {chunk_index+1}/{total_chunks}: Speech not recognized")
                return chunk_index, ""
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return chunk_index, ""
    finally:
        # Clean up temporary file
        if os.path.exists(chunk_filename):
            os.remove(chunk_filename)

def transcribe_audio_file(audio_path, output_path, progress_callback=None):
    """Transcribe audio file to text using parallel processing"""
    try:
        # Load audio file
        sound = AudioSegment.from_file(audio_path)
        
        # Split audio where silence is detected
        chunks = split_on_silence(
            sound,
            min_silence_len=500,
            silence_thresh=sound.dBFS-14,
            keep_silence=500
        )
        
        if not chunks:
            chunks = [sound]
        
        print(f"Audio split into {len(chunks)} chunks")
        
        # Setup multiprocessing
        manager = Manager()
        lock = manager.Lock()
        pool = mp.Pool(processes=mp.cpu_count())
        progress_file = output_path + '.progress'
        
        # Load previous progress
        progress = load_progress(progress_file)
        start_chunk = progress['last_chunk'] + 1
        
        # Prepare chunks for processing
        chunk_data = [
            (chunk, i, len(chunks), progress_file, lock, progress_callback)
            for i, chunk in enumerate(chunks[start_chunk:], start=start_chunk)
        ]
        
        # Process chunks in parallel
        results = pool.map(process_chunk, chunk_data)
        pool.close()
        pool.join()
        
        # Load final progress
        final_progress = load_progress(progress_file)
        all_text = final_progress['transcribed_text']
        
        # Combine all text in order
        final_text = []
        for i in range(len(chunks)):
            if str(i) in all_text and all_text[str(i)]:
                final_text.append(all_text[str(i)])
        
        # Write final transcription
        with open(output_path, "w") as file:
            file.write(" ".join(final_text))
        
        # Remove progress file after successful completion
        if os.path.exists(progress_file):
            os.remove(progress_file)
            
        print(f"Transcription saved to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Transcribe audio to text')
    parser.add_argument('audio_path', help='Path to the .m4a audio file')
    parser.add_argument('-o', '--output', help='Output text file path (default: transcription.txt)')
    
    args = parser.parse_args()
    
    audio_path = args.audio_path
    output_path = args.output if args.output else "transcription.txt"
    
    # Check if audio file exists
    if not os.path.isfile(audio_path):
        print(f"Error: Audio file '{audio_path}' not found")
        return
    
    # Check if file is .m4a
    if not audio_path.lower().endswith('.m4a'):
        print("Error: Only .m4a audio files are supported")
        return
    
    # Transcribe audio
    print("Starting transcription...")
    if not transcribe_audio_file(audio_path, output_path):
        return
    
    print("Transcription complete!")

if __name__ == "__main__":
    main()