import librosa
import numpy as np
from utils import log_error

def extract_trendy_parts(audio_file):
    try:
        # Load the audio file
        y, sr = librosa.load(audio_file)

        # Extract tempo and beat frames
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

        # Extract additional features
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        mfcc = librosa.feature.mfcc(y=y, sr=sr)

        # Combine features into a single matrix
        features = np.vstack([spectral_contrast, chroma, mfcc])

        # Calculate the mean and variance of the features
        feature_mean = np.mean(features, axis=1)
        feature_var = np.var(features, axis=1)

        # Identify the most "trendy" parts based on feature variance
        trendy_indices = np.argsort(feature_var)[-2:]  # Get indices of the two highest variances
        start_time = beat_frames[trendy_indices[0]] if len(beat_frames) > trendy_indices[0] else 0
        end_time = beat_frames[trendy_indices[1]] if len(beat_frames) > trendy_indices[1] else len(y) / sr

        return start_time, end_time
    except Exception as e:
        log_error(f"Error in extract_trendy_parts: {e}")
        return None

def analyze_audio(youtube_link):
    from utils import download_audio, convert_audio_to_wav

    try:
        # Download the audio from YouTube
        audio_file = download_audio(youtube_link, output_path='audio.mp3')
        if not audio_file:
            log_error("Failed to download audio.")
            return None

        # Handle the extra .mp3 extension
        mp3_file = 'audio.mp3.mp3'

        # Convert the audio to WAV format
        wav_file = convert_audio_to_wav(mp3_file, output_path='audio.wav')
        if not wav_file:
            log_error("Failed to convert audio to WAV.")
            return None

        # Extract trendy parts from the audio
        return extract_trendy_parts(wav_file)
    except Exception as e:
        log_error(f"Error in analyze_audio: {e}")
        return None