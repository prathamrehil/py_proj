import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

def download_file(url, folder=os.path.join(os.path.expanduser("~"), "Downloads")):
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        filename = os.path.join(folder, url.split("/")[-1])
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
        if filename.endswith('.zip'):
            extract_zip(filename, folder)
        return filename
    else:
        print(f"Failed to download file from: {url}")
        return None

def extract_zip(zip_path, extract_folder):
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)
    print(f"Extracted: {zip_path}")

def display_files_with_buttons(file_links, site_url):
    print("List of files:")
    for idx, link in enumerate(file_links, start=1):
        file_name = link['href'].split("/")[-1]
        print(f"{idx}. {file_name}")

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

    display_files_with_buttons(file_links, site_url)

    download_option = input("Enter the file number to download, 'all' to download all files, or 'exit' to exit: ")

    if download_option.lower() == 'all':
        download_all_files(file_links, site_url)
    elif download_option.isdigit() and 1 <= int(download_option) <= len(file_links):
        selected_file = file_links[int(download_option) - 1]
        full_url = urljoin(site_url, selected_file['href'])
        download_file(full_url)
    elif download_option.lower() == 'exit':
        print("Exiting.")
    else:
        print("Invalid option. Exiting.")

def download_all_files(file_links, site_url):
    downloaded_files = []
    for link in file_links:
        full_url = urljoin(site_url, link['href'])
        downloaded_file = download_file(full_url)
        if downloaded_file:
            downloaded_files.append(downloaded_file)
    print("Downloaded all files.")

if __name__ == "__main__":
    site_url = input("Enter the URL: ")
    extract_and_download_files(site_url)
