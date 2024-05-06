import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

downloaded_files = set()

def download_file(url, folder='downloads'):
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        filename = os.path.join(folder, url.split("/")[-1])
        if filename not in downloaded_files:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
            downloaded_files.add(filename)
            if filename.endswith('.zip'):
                extract_zip(filename, folder)
    else:
        print(f"Failed to download file from: {url}")

def extract_zip(zip_path, extract_folder):
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)
    print(f"Extracted: {zip_path}")

def extract_and_download_files(site_url):
    response = requests.get(site_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {site_url}. HTTP Status Code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    file_links = soup.select("a[href$='.pdf'], a[href$='.zip']")

    if not file_links:
        print("No PDF or ZIP files found on the page.")
        return

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    for link in file_links:
        full_url = urljoin(site_url, link['href'])
        if "ncert" in full_url.lower():
            download_file(full_url)

if __name__ == "__main__":
    site_url = "https://byjus.com/ncert-books/"
    extract_and_download_files(site_url)
