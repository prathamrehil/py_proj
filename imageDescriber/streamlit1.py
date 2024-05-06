import streamlit as st
import json
import os

with open('image_data_with_nearby_paragraphs.json', 'r') as file:
    data = json.load(file)

filtered_data = [entry for entry in data if entry['dimensions']['width'] > 120 and entry['dimensions']['height'] > 100]

def display_filtered_images(filtered_data):
    for entry in filtered_data:
        if os.path.exists(entry['path']):
            st.image(entry['path'], caption=entry['filename'], width=200)
            st.subheader('Nearby Paragraphs:')
            selected_paragraphs = []
            unselected_paragraphs = entry['nearby_paragraph_chunks'][:]
            for paragraph in entry['nearby_paragraph_chunks']:
                if paragraph not in selected_paragraphs:
                    checkbox_key = f"{entry['filename']}_{paragraph}"
                    selected = st.checkbox(paragraph, value=False, key=checkbox_key)
                    if selected:
                        selected_paragraphs.append(paragraph)
                        unselected_paragraphs.remove(paragraph)
            if selected_paragraphs:
                st.title("Selected paragraphs")
                for paragraph in selected_paragraphs:
                    st.write(paragraph)
            st.write("Dimensions:", entry['dimensions'])
            st.write("Coordinates:", entry['coordinates'])
            st.markdown("---")
        else:
            st.write("Image not found:", entry['filename'])

display_filtered_images(filtered_data)
