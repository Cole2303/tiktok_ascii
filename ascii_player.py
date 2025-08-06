import os
import sys
import subprocess
import cv2
import numpy as np
import time
import hashlib

ASCII_CHARS = np.asarray([' ', '.', ':', '-', '=', '+', '*', '#', '%', '@'])

def download_tiktok(url, output):
    print(f"Downloading TikTok video from {url} ...")
    cmd = ["yt-dlp", "-f", "mp4", "-o", output, url]
    subprocess.run(cmd, check=True)
    print(f"Video downloaded to {output}")

def frame_to_ascii(frame, width=80, height_scale=2.0):
    chars = ASCII_CHARS

    h, w = frame.shape
    aspect_ratio = w / h
    new_height = max(1, int(width / aspect_ratio / height_scale))
    resized = cv2.resize(frame, (width, new_height), interpolation=cv2.INTER_NEAREST)

    # Normalize pixels to range [0, len(chars) - 1]
    normalized = (resized.astype(np.float32) / 255) * (len(chars) - 1)
    indices = normalized.astype(int)

    lines = []
    for row in indices:
        line = "".join(chars[p] for p in row)
        lines.append(line)
    return "\n".join(lines)

def play_video_ascii(video_path, width=80, height_scale=2.0):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 24
    frame_duration = 1.0 / fps

    frame_count = 0
    start_time = time.time()

    try:
        while True:
            frame_start = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ascii_frame = frame_to_ascii(gray, width, height_scale)

            print("\033[H", end="")
            print(ascii_frame)

            frame_count += 1
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                print(f"\nFPS: {frame_count / elapsed:.2f}")

            elapsed = time.time() - frame_start
            sleep_time = frame_duration - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        cap.release()

def generate_unique_filename(url: str) -> str:
    video_id = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"video_{video_id}.mp4"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tiktok_ascii.py <TikTok URL> ")
        sys.exit(1)

    url = sys.argv[1]

    width = 100
    height_scale =  2.4

    video_file = generate_unique_filename(url)

    try:
        download_tiktok(url, video_file)
        play_video_ascii(video_file, width=width, height_scale=height_scale)
    except Exception as e:
        print(f"Error: {e}")
