import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

def extract_links(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a', href=True)]
        return links
    except Exception as e:
        st.error("Error occurred while extracting links:", e)
        return []

def filter_links_with_keyword(links, base_url, keyword):
    filtered_links = []
    for link in links:
        if link.startswith('http') and base_url in link and re.search(r'(?<!s)' + re.escape(keyword) + r'(?!\w)', link):
            filtered_links.append(link)
    return filtered_links


def main():
    st.title("Link Extractor")

    url = st.text_input("Enter the URL to search for links:")
    keyword = "formula"

    if st.button("Extract Links"):
        if url:
            st.info("Extracting links...")
            try:
                links = extract_links(url)
                base_url = url.split("//")[-1].split("/")[0]  # Extracting base URL
                filtered_links = filter_links_with_keyword(links, base_url, keyword)
                for link in filtered_links:
                    st.write("Link:", link)
                    
            except Exception as e:
                st.error("Error occurred while extracting links:", e)
        else:
            st.warning("Please enter a valid URL.")

if __name__ == "__main__":
    main()
