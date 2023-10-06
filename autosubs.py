import os
import time
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import whisper
import subprocess

print("[STATUS] Loading model...")
model = whisper.load_model('large')
print("[STATUS] Model loaded!")

def on_drop(event):
    selected_filepath = event.data

    filename = os.path.basename(selected_filepath)
    filename_label.config(text=f"Filename: {filename}")
    
    print(f"[STATUS] Transcribing file: {filename}...")
    
    start_time = time.time()  # Recording the start time
    result = model.transcribe(selected_filepath, language='en')
    elapsed_time = time.time() - start_time  # Calculating elapsed time
    
    transcription_segments = result['segments']
    print(f"[STATUS] Transcription complete! Took {elapsed_time:.2f} seconds.")

    print("[STATUS] Saving as SRT...")
    srt_content = convert_to_srt(transcription_segments)
    save_path = os.path.splitext(selected_filepath)[0] + '.srt'
    with open(save_path, "w", encoding="utf-8") as file:
        file.write(srt_content)
    print(f"[STATUS] SRT saved to: {save_path}")

    # Embed the subtitles into the video using FFmpeg
    print("[STATUS] Embedding subtitles into video...")
    embed_subtitles(selected_filepath, save_path, selected_filepath)
    print(f"[STATUS] Video with subtitles saved to: {selected_filepath}")

    result_label.config(text=f"Transcription saved as: {save_path}\nVideo with subtitles updated!")

def embed_subtitles(video_file, subtitle_file, output_file):
    cmd = [
        'ffmpeg', 
        '-i', video_file, 
        '-vf', f"subtitles={subtitle_file}", 
        '-c:a', 'copy',  # Copies audio stream without re-encoding
        output_file
    ]
    subprocess.run(cmd)

def convert_to_srt(segments):
    srt_format = ""
    for segment in segments:
        start_time = format_time(segment['start'])
        end_time = format_time(segment['end'])
        srt_format += f"{segment['id'] + 1}\n"
        srt_format += f"{start_time} --> {end_time}\n"
        srt_format += segment['text'] + "\n\n"
    return srt_format

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

root = TkinterDnD.Tk()
root.title("Transcription App")
root.geometry("400x400")

drag_and_drop_label = tk.Label(root, text="Drag and drop an audio file here", bg='lightgray', fg='black', relief=tk.RIDGE)
drag_and_drop_label.pack(pady=50, padx=50, fill=tk.BOTH, expand=True)

filename_label = tk.Label(root, text="Filename: None")
filename_label.pack(pady=10)

result_label = tk.Label(root, text="Transcription: Not available")
result_label.pack(pady=20, fill=tk.BOTH, expand=True)

drag_and_drop_label.drop_target_register(DND_FILES)
drag_and_drop_label.dnd_bind('<<Drop>>', on_drop)

root.mainloop()
