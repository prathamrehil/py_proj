import streamlit as st
import os
from PIL import Image
import re
from youtube_transcript_api import YouTubeTranscriptApi
import yaml
from datetime import timedelta
from pytube import YouTube
from moviepy.editor import VideoFileClip

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
        main_folder = f"{cleaned_video_id}_output"
        os.makedirs(main_folder, exist_ok=True)

        # Initialize a list to store each dialogue with its keyframe and timestamp
        dialogues_data = []

        current_dialogue = {'text': '', 'start_time': 0, 'end_time': 0, 'keyframe_path': None}

        for entry in transcript_data:
            if not current_dialogue['text']:
                current_dialogue['start_time'] = entry['start']
            current_dialogue['text'] += ' ' + entry['text']
            current_dialogue['end_time'] = entry['start'] + entry['duration']

            # Check if the current dialogue ends with '.', '?', or '!'
            if re.search(r'[.!?]$', entry['text']):
                # Save the current dialogue
                dialogues_data.append(current_dialogue.copy())
                current_dialogue = {'text': '', 'start_time': 0, 'end_time': 0, 'keyframe_path': None}

        output_file_path = os.path.join(main_folder, f"{cleaned_video_id}_output_transcript.txt")
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write('\n'.join([f"{format_timestamp(entry['start_time'])} - {entry['text']}" for entry in dialogues_data]))

        print(f"Converted transcript saved to {output_file_path}")

        yaml_output_file_path = os.path.join(main_folder, f"{cleaned_video_id}_output_transcript.yaml")
        create_yaml_file(yaml_output_file_path, dialogues_data)

        output_folder = os.path.join(main_folder, f"{cleaned_video_id}_keyframes")
        os.makedirs(output_folder, exist_ok=True)

        # Download keyframes for all dialogues and update keyframe paths in the dialogues_data
        download_keyframes(video_id, dialogues_data, output_folder)

        download_video(video_id, os.path.join(main_folder, f"{cleaned_video_id}_video.mp4"))

        return dialogues_data  # Return the dialogues_data

    except FileNotFoundError:
        print("Error: File not found or directory does not exist.")
    except PermissionError:
        print("Error: Permission denied. Check if you have the necessary permissions to write to the specified directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    return None

def create_yaml_file(output_file_path, data):
    try:
        with open(output_file_path, 'w', encoding='utf-8') as yaml_file:
            yaml.dump(data, yaml_file, default_flow_style=False)

        print(f"YAML file saved to {output_file_path}")
    except PermissionError:
        print("Error: Permission denied. Check if you have the necessary permissions to write to the specified directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def download_keyframes(video_id, dialogues_data, output_folder):
    try:
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        video_stream = yt.streams.filter(file_extension="mp4").first()
        video_path = video_stream.download()

        with VideoFileClip(video_path) as video_clip:
            for dialogue_info in dialogues_data:
                timestamp = dialogue_info['start_time']
                frame_path = os.path.join(output_folder, f"{format_timestamp(timestamp).replace(':', '_')}.jpg")
                video_clip.save_frame(frame_path, t=timestamp)

                # Update the keyframe path in the dialogues_data
                dialogue_info['keyframe_path'] = frame_path

        print(f"Keyframes downloaded to {output_folder}")

        # Clean up: Remove temporary video file
        os.remove(video_path)

    except Exception as e:
        print(f"An unexpected error occurred while downloading keyframes: {str(e)}")

def download_video(video_id, output_path):
    try:
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        yt.streams.filter(file_extension="mp4").first().download(output_path)
        print(f"Video downloaded to {output_path}")
    except Exception as e:
        print(f"An unexpected error occurred while downloading the video: {str(e)}")

def load_transcript_from_yaml(yaml_path):
    try:
        with open(yaml_path, 'r', encoding='utf-8') as yaml_file:
            dialogues_data = yaml.safe_load(yaml_file)

            if isinstance(dialogues_data, list) and all(isinstance(entry, dict) for entry in dialogues_data):
                return dialogues_data
            else:
                raise ValueError("Invalid format in YAML file")

    except FileNotFoundError:
        st.error("Error: Transcript file not found.")
    except Exception as e:
        st.error(f"An unexpected error occurred while loading transcript: {str(e)}")
        return None

def display_dialogue_and_keyframe(cleaned_video_id, dialogues_data, index):
    if dialogues_data is not None:

        if isinstance(dialogues_data, list):
            try:
                if index < len(dialogues_data):
                    current_dialogue = dialogues_data[index]

                    st.header("Dialogue:")
                    st.write(current_dialogue['text'])
                    st.header("Time Frame:")
                    st.write(f"Start: {format_timestamp(current_dialogue['start_time'])} - End: {format_timestamp(current_dialogue['end_time'])}")

                    keyframe_path = current_dialogue.get('keyframe_path')

                    if keyframe_path and os.path.exists(keyframe_path):
                        keyframe_image = Image.open(keyframe_path)
                        st.image(keyframe_image, caption='Keyframe', use_column_width=True)
                    else:
                        st.warning("Keyframe image not found.")

                else:
                    st.warning("No more dialogues to display.")

            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
        elif isinstance(dialogues_data, dict):
            st.warning("Transcript data is not in the expected list format.")
        else:
            st.warning("Unknown format of transcript data.")
    else:
        st.warning("Transcript data is not available.")

def main():
    st.title("YouTube Transcript Viewer")

    cleaned_video_id = None  # Initialize cleaned_video_id outside the if block

    # Get YouTube link from user input
    yt_link = st.text_input('Enter the YouTube link:')

    # Define a unique key based on the YouTube link
    button_key = f"button_{hash(yt_link)}"

    # Fetch button
    if st.button('Fetch', key=button_key):
        try:
            video_id = extract_video_id(yt_link)
            cleaned_video_id = clean_video_id(video_id)
            transcript_data = get_transcript(video_id)

            if transcript_data:
                dialogues_data = save_transcript_to_text_and_yaml(video_id, transcript_data, cleaned_video_id)

                # Initialize the index in session state
                st.session_state.index = 0
                st.session_state.dialogues_data = dialogues_data

        except ValueError as ve:
            st.error(f"Error: {str(ve)}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

    # Display the current dialogue and keyframe
    if 'index' in st.session_state and 'dialogues_data' in st.session_state:
        display_dialogue_and_keyframe(cleaned_video_id, st.session_state.dialogues_data, st.session_state.index)

        # Display Previous and Next buttons
        col1, col2, col3 = st.columns([2, 6, 2])

        if col1.button('Previous') and st.session_state.index > 0:
            st.session_state.index -= 1
            
        if col3.button('Next') and st.session_state.index < len(st.session_state.dialogues_data) - 1:
            st.session_state.index += 1

if __name__ == "__main__":
    main()
