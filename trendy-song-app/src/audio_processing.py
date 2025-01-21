import librosa
import numpy as np
import os
from utils import log_error, download_audio, convert_audio_to_wav

def extract_trendy_parts(audio_file):
    try:
        # Load the audio file
        y, sr = librosa.load(audio_file)

        # Extract tempo and beat frames
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

        # Calculate the onset envelope
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)

        # Calculate the energy of each beat
        beat_energy = librosa.util.sync(onset_env, beat_frames, aggregate=np.median)

        # Find the beat with the highest energy
        max_energy_idx = np.argmax(beat_energy)

        # Define the window around the most energetic beat
        window_size = 4  # Number of beats before and after the most energetic beat
        start_idx = max(0, max_energy_idx - window_size)
        end_idx = min(len(beat_frames) - 1, max_energy_idx + window_size)

        # Convert beat frames to timestamps
        start_time = librosa.frames_to_time(beat_frames[start_idx], sr=sr)
        end_time = librosa.frames_to_time(beat_frames[end_idx], sr=sr)

        return float(start_time), float(end_time)
    except Exception as e:
        log_error(f"Error in extract_trendy_parts: {e}")
        return None

def analyze_audio(youtube_link):
    try:
        # Download the audio from YouTube
        audio_file = download_audio(youtube_link)
        if not audio_file:
            log_error("Failed to download audio.")
            return None

        # Convert the audio to WAV format
        wav_file = convert_audio_to_wav(audio_file)
        if not wav_file:
            log_error("Failed to convert audio to WAV.")
            return None

        # Extract trendy parts from the audio
        timestamps = extract_trendy_parts(wav_file)

        # Clean up temporary files
        os.remove(audio_file)
        os.remove(wav_file)

        return timestamps
    except Exception as e:
        log_error(f"Error in analyze_audio: {e}")
        return None