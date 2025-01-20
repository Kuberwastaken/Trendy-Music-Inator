import torch
import librosa
import numpy as np
from demucs.pretrained import get_model
from demucs.apply import apply_model
import warnings
import os
from pydub import AudioSegment
warnings.filterwarnings('ignore')

class SongHookDetector:
    def __init__(self):
        print("Initializing models (this may take a moment)...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        print("Loading Demucs model...")
        self.separator = get_model('htdemucs')
        self.separator.to(self.device)
        print("Models loaded successfully!")
    
    def load_and_separate_vocals(self, file_path):
        audio, sr = librosa.load(file_path, sr=44100, mono=True)
        audio = torch.tensor(audio).reshape(1, -1)
        
        ref = audio.mean(0)
        sources = apply_model(self.separator, ref.reshape(1, -1), progress=True)
        vocals = sources[0, 0].numpy()
        
        return vocals, sr
    
    def compute_hook_features(self, audio, sr):
        hop_length = 512
        frame_length = 2048
        
        # RMS Energy (loudness)
        rms = librosa.feature.rms(y=audio, hop_length=hop_length)[0]
        
        # Spectral Centroid (brightness/intensity)
        spectral_centroids = librosa.feature.spectral_centroid(
            y=audio, 
            sr=sr, 
            hop_length=hop_length
        )[0]
        
        # Onset Strength (rhythmic changes)
        onset_env = librosa.onset.onset_strength(
            y=audio, 
            sr=sr,
            hop_length=hop_length
        )
        
        # Mel Spectrogram (energy distribution)
        mel_spec = librosa.feature.melspectrogram(
            y=audio, 
            sr=sr,
            n_mels=128,
            hop_length=hop_length
        )
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        mel_mean = np.mean(mel_spec_db, axis=0)
        
        # Normalize features
        rms_norm = (rms - rms.min()) / (rms.max() - rms.min() + 1e-6)
        cent_norm = (spectral_centroids - spectral_centroids.min()) / (spectral_centroids.max() - spectral_centroids.min() + 1e-6)
        onset_norm = (onset_env - onset_env.min()) / (onset_env.max() - onset_env.min() + 1e-6)
        mel_norm = (mel_mean - mel_mean.min()) / (mel_mean.max() - mel_mean.min() + 1e-6)
        
        # Combine features with weights
        combined_score = (
            0.4 * rms_norm +      # Emphasize loudness
            0.2 * cent_norm +     # Consider timbral changes
            0.2 * onset_norm +    # Account for rhythmic changes
            0.2 * mel_norm        # Overall spectral content
        )
        
        return combined_score, hop_length
    
    def find_hooks(self, file_path, min_duration=5, max_duration=15):
        vocals, sr = self.load_and_separate_vocals(file_path)
        combined_score, hop_length = self.compute_hook_features(vocals, sr)
        
        peaks = librosa.util.peak_pick(
            combined_score,
            pre_max=20,
            post_max=20,
            pre_avg=20,
            post_avg=20,
            delta=0.3,
            wait=10
        )
        
        hooks = []
        for peak in peaks:
            start_time = librosa.samples_to_time(peak * hop_length, sr=sr)
            
            duration = min_duration
            peak_score = combined_score[peak]
            i = peak
            while i < len(combined_score) and duration < max_duration:
                if combined_score[i] < peak_score * 0.5:
                    break
                duration = librosa.samples_to_time((i - peak) * hop_length, sr=sr)
                i += 1
            
            hooks.append({
                'start_time': float(start_time),
                'duration': float(duration),
                'confidence': float(combined_score[peak])
            })
        
        hooks.sort(key=lambda x: x['confidence'], reverse=True)
        return hooks[:3]

    def extract_segment(self, input_file, start_time, duration, output_file):
        audio = AudioSegment.from_file(input_file)
        start_ms = int(start_time * 1000)
        duration_ms = int(duration * 1000)
        segment = audio[start_ms:start_ms + duration_ms]
        segment.export(output_file, format="mp3")
        return output_file

def main():
    # Check for FFmpeg
    try:
        AudioSegment.from_file(os.devnull)
    except Exception as e:
        print("Error: FFmpeg is not properly installed. Please install FFmpeg first.")
        print("Windows: Use 'choco install ffmpeg' or download from https://github.com/BtbN/FFmpeg-Builds/releases")
        print("Mac: Use 'brew install ffmpeg'")
        print("Linux: Use 'sudo apt-get install ffmpeg'")
        return

    # Get input file from command line or use default
    input_file = input("Enter the name of your MP3 file (e.g., song.mp3): ").strip()
    
    if not input_file:
        print("Error: No file name provided")
        return
        
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found in the current directory")
        return
        
    print(f"\nProcessing file: {input_file}")
    
    # Create detector and process file
    try:
        detector = SongHookDetector()
        hooks = detector.find_hooks(input_file)
        
        print("\nDetected hooks:")
        for i, hook in enumerate(hooks, 1):
            print(f"\nHook {i}:")
            print(f"Start time: {hook['start_time']:.2f} seconds")
            print(f"Duration: {hook['duration']:.2f} seconds")
            print(f"Confidence: {hook['confidence']:.2%}")
            
            output_file = f"hook_{i}.mp3"
            detector.extract_segment(
                input_file, 
                hook['start_time'], 
                hook['duration'], 
                output_file
            )
            print(f"Saved hook segment to: {output_file}")
            
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure FFmpeg is properly installed")
        print("2. Ensure the input file is a valid MP3 file")
        print("3. Try with a different MP3 file")

if __name__ == "__main__":
    main()