import streamlit as st
import os
import pdfplumber
import json
from math import sqrt
from PIL import Image

# @st.cache_data
def distance(x1, y1, x2, y2):
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# @st.cache_data
def extract_paragraph_chunks(text, start_keywords=['Let', 'Alternatively', 'Given', 'In a','In the', 'Having', 'Consider', 'Conversely', 'Now'], end_keyword='.'):
    lines = text.split('\n')
    chunks = []
    current_chunk = ""

    for line in lines:
        if any(line.strip().startswith(keyword) for keyword in start_keywords):
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line.strip()
        elif end_keyword in line:
            current_chunk += " " + line.strip()
            if current_chunk.endswith('.'):
                chunks.append(current_chunk.strip())
                current_chunk = ""
        elif '.' in line:
            chunks.append(line.strip())
        else:
            current_chunk += " " + line.strip()

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# @st.cache_data
def load_and_extract_data(pdf_path):
    output_directory = 'imgs/'
    os.makedirs(output_directory, exist_ok=True)
    images_data = []

    with pdfplumber.open(pdf_path) as pdf_obj:
        for page_number, page in enumerate(pdf_obj.pages):
            images_in_page = page.images
            texts = page.extract_text()
            paragraph_chunks = extract_paragraph_chunks(texts)
            page_height = page.height

            for i, image in enumerate(images_in_page):
                image_bbox = (image['x0'], page_height - image['y1'], image['x1'], page_height - image['y0'])
                x_mid = (image['x0'] + image['x1']) / 2
                y_mid = (image['y0'] + image['y1']) / 2

                nearby_paragraphs = []
                for chunk in paragraph_chunks:
                    if 'Fig' in chunk:
                        x_para = (image['x0'] + image['x1']) / 2
                        y_para = (image['y0'] + image['y1']) / 2
                        if distance(x_mid, y_mid, x_para, y_para) < 100:
                            nearby_paragraphs.append(chunk)

                if nearby_paragraphs:
                    image_obj = page.crop(image_bbox).to_image(resolution=400)
                    image_filename = f'page_{page_number+1}_image_{i+1}.png'
                    image_path = os.path.join(output_directory, image_filename)
                    image_obj.save(image_path)
                    images_data.append({
                        'filename': image_filename,
                        'path': image_path,
                        'dimensions': {
                            'width': image['width'],
                            'height': image['height']
                        },
                        'coordinates': {
                            'x0': image['x0'],
                            'y0': image['y0'],
                            'x1': image['x1'],
                            'y1': image['y1']
                        },
                        'nearby_paragraph_chunks': nearby_paragraphs
                    })
    return images_data
# △
def main():
    st.title("Image Describer From PDF")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    selected_data = []

    if uploaded_file is not None:
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        images_data = load_and_extract_data("temp.pdf")
        with st.spinner("Loading images..."):
            for entry in images_data:
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
                        selected_data.append({
                            'filename': entry['filename'],
                            'image_path': entry['path'],
                            'selected_paragraphs': selected_paragraphs
                        })
                    st.write("Dimensions:", entry['dimensions'])
                    st.write("Coordinates:", entry['coordinates'])
                    st.markdown("---")
                else:
                    st.write("Image not found:", entry['filename'])        
        if selected_data:
            if st.button("Show JSON for Selected Data"):
                json_data = json.dumps(selected_data, indent=4)
                st.text_area("JSON Output", json_data, height=500)
                st.download_button(label="Download JSON", data=json_data, file_name="selected_data.json", mime="application/json")

if __name__ == "__main__":
    main()
