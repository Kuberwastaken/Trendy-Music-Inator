import subprocess

def download_audio(youtube_url, output_path='audio.mp3'):
    import yt_dlp
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                'nopostoverwrites': False,
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return output_path
    except Exception as e:
        log_error(f"Error downloading audio: {e}")
        return None

def convert_audio_to_wav(input_path, output_path='audio.wav'):
    try:
        subprocess.run(['ffmpeg', '-i', input_path, output_path], check=True)
        return output_path
    except Exception as e:
        log_error(f"Error converting audio: {e}")
        return None

def log_error(message):
    with open('error.log', 'a') as log_file:
        log_file.write(message + '\n')