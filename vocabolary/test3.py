import requests
from bs4 import BeautifulSoup
import re
import streamlit as st

def main():
    st.title("Physics Formulas")
    url = 'https://www.pw.live/exams/school/math-formulas/'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        pattern = re.compile(r".*=.*")
        list_items = soup.find_all('li', text=pattern)
        st.markdown("**Formulas:**")
        for idx, li in enumerate(list_items, start=1):
            st.markdown(f"<p style='font-size: 20px; margin-bottom: 10px;'><b>{idx}. {li.get_text()}</b></p>", unsafe_allow_html=True)
            st.text("")  
    else:
        st.error("Failed to retrieve the webpage")

if __name__ == "__main__":
    main()
