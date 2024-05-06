import os
import pdfplumber
import json
from math import sqrt

def distance(x1, y1, x2, y2):
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

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


pdf_path = 'ncert-textbook-for-class-11-maths-chapter-11.pdf'
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
                    if distance(x_mid, y_mid, x_para, y_para) < 100:  # Adjust threshold as needed
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

json_filename = 'image_data_with_nearby_paragraphs.json'
with open(json_filename, 'w') as json_file:
    json.dump(images_data, json_file, indent=4)

print(f'JSON file "{json_filename}" created with image data including nearby paragraph chunks.')
