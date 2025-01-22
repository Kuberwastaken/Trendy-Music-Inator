import subprocess
import os
import tempfile
import yt_dlp

def download_audio(youtube_url):
    try:
        temp_dir = tempfile.mkdtemp()
        temp_output_path = os.path.join(temp_dir, 'audio.mp3')
        ydl_opts = {
            'format': 'worstaudio/worst',
            'outtmpl': temp_output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '64',  # Lower quality for faster processing
                'nopostoverwrites': False,
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        
        # Handle the extra .mp3 extension
        final_output_path = temp_output_path + '.mp3'
        if os.path.exists(final_output_path):
            os.rename(final_output_path, temp_output_path)
        
        return temp_output_path
    except Exception as e:
        log_error(f"Error downloading audio: {e}")
        return None

def convert_audio_to_wav(input_path):
    try:
        output_path = input_path.replace('.mp3', '.wav')
        subprocess.run(['ffmpeg', '-i', input_path, output_path], check=True)
        return output_path
    except Exception as e:
        log_error(f"Error converting audio: {e}")
        return None

def log_error(message):
    with open('error.log', 'a') as log_file:
        log_file.write(message + '\n')