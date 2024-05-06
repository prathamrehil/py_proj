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

@st.cache_data
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"Error retrieving transcript: {str(e)}")
        return None

@st.cache_data
def save_transcript_to_text_and_yaml(video_id, transcript_data, cleaned_video_id):
    try:
        main_folder = f"{cleaned_video_id}_output"
        os.makedirs(main_folder, exist_ok=True)

        dialogues_data = []

        for entry in transcript_data:
            timestamp = format_timestamp(entry['start'])

            dialogue_info = {
                'text': entry['text'],
                'start_time': entry['start'],
                'end_time': entry['start'] + entry['duration'],
                'keyframe_path': None
            }

            dialogues_data.append(dialogue_info)

        output_file_path = os.path.join(main_folder, f"{cleaned_video_id}_output_transcript.txt")
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write('\n'.join([f"{format_timestamp(entry['start_time'])} - {entry['text']}" for entry in dialogues_data]))

        print(f"Converted transcript saved to {output_file_path}")

        yaml_output_file_path = os.path.join(main_folder, f"{cleaned_video_id}_output_transcript.yaml")
        create_yaml_file(yaml_output_file_path, dialogues_data)

        output_folder = os.path.join(main_folder, f"{cleaned_video_id}_keyframes")
        os.makedirs(output_folder, exist_ok=True)

        download_keyframes(video_id, dialogues_data, output_folder)

        download_video(video_id, os.path.join(main_folder, f"{cleaned_video_id}_video.mp4"))

        return dialogues_data

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

@st.cache_data
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
                dialogue_info['keyframe_path'] = frame_path

        print(f"Keyframes downloaded to {output_folder}")

        os.remove(video_path)

    except Exception as e:
        print(f"An unexpected error occurred while downloading keyframes: {str(e)}")


# def resize_keyframe(keyframe_path, size, compression_quality=95):
#     try:
#         img = Image.open(keyframe_path)
#         img = img.convert('RGB')
#         resized_img = img.resize(size, Image.LANCZOS)
#         resized_img.save(keyframe_path, format='JPEG', quality=compression_quality)
#     except Exception as e:
#         print(f"Error resizing keyframe: {str(e)}")



@st.cache_data
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

                    st.subheader("Dialogue:")
                    st.write(current_dialogue['text'])

                    st.subheader("Time Frame:")
                    st.write(f"Start: {format_timestamp(current_dialogue['start_time'])} - End: {format_timestamp(current_dialogue['end_time'])}")

                    keyframe_path = current_dialogue.get('keyframe_path')

                    if keyframe_path and os.path.exists(keyframe_path):
                        keyframe_image = Image.open(keyframe_path)

                        # Set the width of the displayed image, use_container_width makes it responsive
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
    st.set_page_config(
        page_title="YouTube Transcript Viewer",
        page_icon=":clapper:",
    )

    # Add custom CSS to adjust page scale
    st.markdown(
        """
        <style>
        body {
            zoom: 0.931;  /* Adjust the zoom factor as needed */
        }
        .stApp {
            zoom: 1.0;  /* Adjust the zoom factor as needed */
        }
        .st-markdown .stSubheader {
            margin-top: -5px;  /* Adjust the top margin for subheaders */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Sidebar for user input
    with st.sidebar:
        st.subheader("Transcript Viewer")
        yt_link = st.text_input('Enter the YouTube link:')
        
        # Wider "Fetch" button
        st.markdown(
            "<style>"
            "div[data-testid='stSidebar'][aria-expanded='true'] button {width: 100%;}"
            "</style>",
            unsafe_allow_html=True
        )
        
        fetch_button_clicked = st.button('Fetch', key='fetch_button')

        # Display "Prev" and "Next" buttons only if fetching is done
        if st.session_state.get('fetching_done', False):
            col_prev, col_next = st.columns([1, 1])

            with col_prev:
                if st.button('Prev') and st.session_state.index > 0:
                    st.session_state.index -= 1

            with col_next:
                if st.button('Next') and st.session_state.index < len(st.session_state.dialogues_data) - 1:
                    st.session_state.index += 1

    # Main content area
    index = st.session_state.get('index', 0)
    dialogues_data = st.session_state.get('dialogues_data', [])
    fetching_done = st.session_state.get('fetching_done', False)
    cleaned_video_id = st.session_state.get('cleaned_video_id', None)

    try:
        if fetch_button_clicked:
            video_id = extract_video_id(yt_link)
            cleaned_video_id = clean_video_id(video_id)

            if not fetching_done:
                st.write("Fetching....")
                transcript_data = get_transcript(video_id)

                if transcript_data:
                    dialogues_data = save_transcript_to_text_and_yaml(video_id, transcript_data, cleaned_video_id)

                    st.session_state.index = 0
                    st.session_state.dialogues_data = dialogues_data
                    st.session_state.fetching_done = True
                    st.session_state.cleaned_video_id = cleaned_video_id
                    st.empty()  # Clear the "Fetching..." message

    except ValueError as ve:
        st.error(f"Error: {str(ve)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

    # Display the current dialogue and keyframe
    if fetching_done and dialogues_data:
        if 0 <= index < len(dialogues_data):
            display_dialogue_and_keyframe(cleaned_video_id, dialogues_data, index)

if __name__ == "__main__":
    main()
