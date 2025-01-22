import librosa
import numpy as np
import scipy
from sklearn.preprocessing import StandardScaler
from scipy.signal import find_peaks
import os
from utils import log_error, download_audio, convert_audio_to_wav

def extract_audio_features(y, sr):
    """Extract multiple audio features for better trend detection."""
    
    # Get various audio features
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    
    # Spectral features
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    
    # RMS energy
    rms = librosa.feature.rms(y=y)[0]
    
    # Mel-frequency spectrogram
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    # Chromagram
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    
    return {
        'onset_env': onset_env,
        'beat_frames': beat_frames,
        'spectral_centroids': spectral_centroids,
        'spectral_rolloff': spectral_rolloff,
        'rms': rms,
        'mel_spec_db': mel_spec_db,
        'chroma': chroma
    }

def calculate_novelty_curve(features):
    """Calculate a novelty curve based on multiple features."""
    
    # Normalize all features
    scaler = StandardScaler()
    
    # Process mel spectrogram for novelty
    mel_novelty = np.diff(features['mel_spec_db'].mean(axis=0))
    mel_novelty = np.pad(mel_novelty, (1, 0))
    
    # Combine RMS energy with onset envelope
    energy_novelty = scaler.fit_transform(features['rms'].reshape(-1, 1)).flatten()
    onset_novelty = scaler.fit_transform(features['onset_env'].reshape(-1, 1)).flatten()
    
    # Calculate chroma novelty
    chroma_novelty = np.sum(np.diff(features['chroma'], axis=1)**2, axis=0)
    chroma_novelty = np.pad(chroma_novelty, (1, 0))
    chroma_novelty = scaler.fit_transform(chroma_novelty.reshape(-1, 1)).flatten()
    
    # Combine all novelty curves
    combined_novelty = (energy_novelty + onset_novelty + chroma_novelty) / 3
    
    return scipy.signal.medfilt(combined_novelty, kernel_size=11)

def find_trendy_segments(novelty_curve, threshold_percentile=85, min_distance_frames=100):
    """Find trendy segments based on the novelty curve."""
    
    # Calculate adaptive threshold
    threshold = np.percentile(novelty_curve, threshold_percentile)
    
    # Find peaks in novelty curve
    peaks, _ = find_peaks(novelty_curve, 
                         height=threshold,
                         distance=min_distance_frames)
    
    # Group nearby peaks into segments
    segments = []
    current_segment = [peaks[0]]
    
    for peak in peaks[1:]:
        if peak - current_segment[-1] < min_distance_frames * 2:
            current_segment.append(peak)
        else:
            segments.append((current_segment[0], current_segment[-1]))
            current_segment = [peak]
    
    segments.append((current_segment[0], current_segment[-1]))
    
    return segments

def extract_trendy_parts(audio_file):
    try:
        # Load the audio file
        y, sr = librosa.load(audio_file, sr=None)
        
        # Extract audio features
        features = extract_audio_features(y, sr)
        
        # Calculate novelty curve
        novelty_curve = calculate_novelty_curve(features)
        
        # Find trendy segments
        segments = find_trendy_segments(novelty_curve)
        
        if not segments:
            return None
        
        # Convert frame indices to timestamps
        start_time = librosa.frames_to_time(segments[0][0], sr=sr)
        end_time = librosa.frames_to_time(segments[-1][1], sr=sr)
        
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