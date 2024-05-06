import json
import re
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
import yaml
from datetime import timedelta
import os
from pytube import YouTube
from moviepy.editor import VideoFileClip
from PIL import Image

def extract_video_id(url):
    try:
        video_id_match = re.search(r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})', url)
        if video_id_match:
            return video_id_match.group(1)
        else:
            raise ValueError("Invalid YouTube URL")
    except Exception as e:
        raise ValueError("Invalid YouTube URL")

def clean_video_id(video_id):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', video_id)

def single_line(paragraph):
    return paragraph.replace('\n', ' ').strip()

def format_timestamp(seconds):
    return str(timedelta(seconds=seconds))

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"Error retrieving transcript: {str(e)}")
        return None

def save_transcript_to_text_and_yaml(video_id, transcript_data, cleaned_video_id):
    try:
        paragraphs = []
        keyframes = []

        current_paragraph = ""
        for entry in transcript_data:
            timestamp = format_timestamp(entry['start'])
            current_line = f"{timestamp} - {entry['text']}"

            if current_line.endswith(('.', '!', '?')):
                paragraphs.append(current_line)
                keyframes.append(timestamp)
                current_paragraph = ""
            else:
                current_paragraph += current_line + ' '

        if current_paragraph:
            paragraphs.append(current_paragraph.strip())

        output_file_path = f"{cleaned_video_id}_output_transcript.txt"
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write('\n'.join([single_line(paragraph) for paragraph in paragraphs]))

        print(f"Converted transcript saved to {output_file_path}")

        yaml_output_file_path = f"{cleaned_video_id}_output_transcript.yaml"
        create_yaml_file(yaml_output_file_path, paragraphs)

        keyframes_file_path = f"{cleaned_video_id}_keyframes.txt"
        with open(keyframes_file_path, 'w', encoding='utf-8') as keyframes_file:
            keyframes_file.write('\n'.join(keyframes))

        print(f"Keyframes file saved to {keyframes_file_path}")

        output_folder = f"{cleaned_video_id}_keyframes"
        os.makedirs(output_folder, exist_ok=True)
        download_keyframes(video_id, keyframes, output_folder)

    except FileNotFoundError:
        print("Error: File not found or directory does not exist.")
    except PermissionError:
        print("Error: Permission denied. Check if you have the necessary permissions to write to the specified directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def create_yaml_file(output_file_path, paragraphs):
    try:
        with open(output_file_path, 'w', encoding='utf-8') as yaml_file:
            yaml.dump(paragraphs, yaml_file, default_flow_style=False)

        print(f"YAML file saved to {output_file_path}")
    except PermissionError:
        print("Error: Permission denied. Check if you have the necessary permissions to write to the specified directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def download_keyframes(video_id, keyframes, output_folder):
    try:
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        for timestamp in keyframes:
            frame_path = os.path.join(output_folder, f"{timestamp.replace(':', '_')}.jpg")
            with VideoFileClip(yt.streams.filter(file_extension="mp4", res="360p").first().download()) as video_clip:
                video_clip.save_frame(frame_path, t=timestamp)

        print(f"Keyframes downloaded to {output_folder}")
    except Exception as e:
        print(f"An unexpected error occurred while downloading keyframes: {str(e)}")

yt_link = input('Enter the YouTube link: ')

try:
    video_id = extract_video_id(yt_link)
    cleaned_video_id = clean_video_id(video_id)
    transcript_data = get_transcript(video_id)

    if transcript_data:
        save_transcript_to_text_and_yaml(video_id, transcript_data, cleaned_video_id)
except ValueError as ve:
    print(f"Error: {str(ve)}")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
