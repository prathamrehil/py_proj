import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import zipfile

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

def download_file(url, folder=os.path.join(os.path.expanduser("~"), "Downloads")):
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        filename = os.path.join(folder, url.split("/")[-1])
        with open(filename, 'wb') as f:
            f.write(response.content)
        st.success(f"Downloaded: {filename}")
        return filename
    else:
        st.error(f"Failed to download file from: {url}")
        return None

def extract_zip(zip_path, extract_folder):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_filename = os.path.splitext(os.path.basename(zip_path))[0]
        extract_path = os.path.join(extract_folder, zip_filename)
        zip_ref.extractall(extract_path)
    st.success(f"Extracted: {zip_path} to {extract_path}")

def display_files_with_buttons(site_url):
    response = requests.get(site_url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch {site_url}. HTTP Status Code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    file_links = soup.select("a[href$='.pdf'], a[href$='.zip']")

    if not file_links:
        st.warning("No PDF or ZIP files found on the page.")
        return

    # Filter file_links to include only those containing 'ncert'
    file_links_ncert = [link for link in file_links if 'ncert' in link['href'].lower()]

    if not file_links_ncert:
        st.warning("No PDF or ZIP files with 'ncert' in the link found on the page.")
        return

    st.button("Download All", on_click=download_all_files, args=(site_url, file_links_ncert))

    st.write("List of files:")
    download_links = []

    for idx, link in enumerate(file_links_ncert, start=1):
        file_name = link['href'].split("/")[-1]
        button_key = f"button_{idx}"

        # Generate the HTML for the download link
        download_links.append(urljoin(site_url, link["href"]))
        st.markdown(
            f'<a href="{urljoin(site_url, link["href"])}" download="{file_name}">Download {file_name}</a>',
            unsafe_allow_html=True
        )

def download_all_files(site_url, file_links):
    downloaded_files = []
    folder = os.path.join(os.path.expanduser("~"), "Downloads")
    for link in file_links:
        full_url = urljoin(site_url, link['href'])
        downloaded_file = download_file(full_url, folder)
        if downloaded_file and downloaded_file.endswith('.zip'):
            extract_zip(downloaded_file, folder)
        if downloaded_file:
            downloaded_files.append(downloaded_file)
    st.success("Downloaded and extracted all files.")
    compress_files(downloaded_files, folder)

def compress_files(files, folder):
    zip_path = os.path.join(folder, "all_files.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files:
            zipf.write(file, os.path.basename(file))
    st.success("Compressed all files into all_files.zip.")

if __name__ == "__main__":
    st.title("Pdf And Zip Extracter")
    site_url = st.text_input("Enter the URL:")
    if st.button("Fetch Pdfs and Zips"):
        display_files_with_buttons(site_url)
