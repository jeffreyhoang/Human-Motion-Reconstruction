import matplotlib.pyplot as plt
import librosa.display
import numpy as np
import ffmpeg
import os

def extract_audio(video_file, audio_file):
    try:
        ffmpeg.input(video_file).output(audio_file, qscale=0, map='a').run()
        print(f"Audio extracted from {video_file} to {audio_file}")
    except Exception as e:
        print(f"Error extracting audio from {video_file}: {e}")

def detect_valid_claps(audio_file, threshold_factor=0.8, max_gap=1.0):
    try:
        y, sr = librosa.load(audio_file, sr=None)

        # Apply a high-pass filter
        y_filtered = librosa.effects.preemphasis(y, coef=0.97)

        # Compute the onset envelope
        onset_env = librosa.onset.onset_strength(y=y_filtered, sr=sr, aggregate=np.median, lag=2)

        # Set the threshold based on a factor of the maximum onset envelope value
        threshold = threshold_factor * np.max(onset_env)

        # Find all peaks above the threshold
        peaks = np.where(onset_env >= threshold)[0]
        peak_times = librosa.frames_to_time(peaks, sr=sr)

        # Identify valid clap triplets (three claps within the max_gap time frame)
        valid_clap_triplets = []
        for i in range(len(peak_times) - 2):
            if (peak_times[i + 1] - peak_times[i] <= max_gap and
                peak_times[i + 2] - peak_times[i + 1] <= max_gap):
                valid_clap_triplets.append((peak_times[i], peak_times[i + 1], peak_times[i + 2]))

        # Ensure there are at least two valid triplets
        if len(valid_clap_triplets) < 2:
            print(f"Insufficient valid clap triplets detected in {audio_file}. Need at least two triplets.")
            return []

        # Use the first clap of the first triplet and the third clap of the last triplet
        start_time = valid_clap_triplets[0][2]
        end_time = valid_clap_triplets[-1][2]

        # Plotting and debugging information
        plt.figure(figsize=(12, 8))

        plt.subplot(2, 1, 1)
        librosa.display.waveshow(y, sr=sr)
        plt.title('Waveform')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Amplitude')

        plt.subplot(2, 1, 2)
        plt.plot(onset_env, label='Onset Strength')
        plt.axhline(y=threshold, color='r', linestyle='--', label=f'Threshold ({threshold_factor * 100}%)')
        plt.vlines([librosa.time_to_frames(t, sr=sr) for t in [start_time, valid_clap_triplets[0][1], valid_clap_triplets[0][2], valid_clap_triplets[-1][0], valid_clap_triplets[-1][1], end_time]], 0, max(onset_env), color='g', linestyle='--', label='Detected Claps')
        plt.title('Onset Envelope with Detected Valid Claps')
        plt.xlabel('Frame')
        plt.ylabel('Onset Strength')
        plt.legend()

        plt.tight_layout()
        plt.show()

        print(f"Valid clap range in {audio_file}: {start_time} to {end_time}")
        return start_time, end_time

    except Exception as e:
        print(f"Error detecting claps in {audio_file}: {e}")
        return []

def sync_videos(video_files, audio_dir, output_dir):
    for video_file in video_files:
        video_name = os.path.basename(video_file)
        audio_file = os.path.join(audio_dir, video_name.replace('.mp4', '.wav'))
        extract_audio(video_file, audio_file)
        time_range = detect_valid_claps(audio_file, threshold_factor=0.8, max_gap=0.5)  # Adjust max_gap as needed

        if time_range:
            start_time, end_time = time_range
            output_file = os.path.join(output_dir, video_name)

            # Trim the video between the valid clap triplets
            try:
                ffmpeg.input(video_file, ss=start_time, to=end_time).output(output_file).run()
                print(f"Video {video_file} synchronized and saved as {output_file}")
            except Exception as e:
                print(f"Error processing {video_file}: {e}")
        else:
            print(f"Insufficient valid clap triplets detected in {video_file}. Skipping this file.")

if __name__ == "__main__":
    video_dir = 'videos'
    audio_dir = 'audio'
    output_dir = 'output'

    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    video_files = [os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith('.mp4')]

    sync_videos(video_files, audio_dir, output_dir)