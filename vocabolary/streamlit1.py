import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

def fetch_formulas(subject):
    if subject == "Physics":
        url = "https://www.pw.live/exams/school/physics-formulas/"
    elif subject == "Chemistry":
        url = "https://www.example.com"
    elif subject == "Maths":
        url = "https://www.pw.live/exams/school/math-formulas/"
    else:
        st.error("Invalid subject selected.")
        return

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        pattern = re.compile(r".*=.*")
        list_items = soup.find_all('li', string=pattern)
        st.markdown("**Formulas:**")
        for idx, li in enumerate(list_items, start=1):
            st.markdown(f"<p style='font-size: 20px; margin-bottom: 10px;'><b>{idx}. {li.get_text()}</b></p>", unsafe_allow_html=True)
            st.text("")  
    else:
        st.error("Failed to retrieve the webpage")

st.title("Formula Dictionary")
selected_subject = st.selectbox("Select Subject", ["Physics", "Chemistry", "Maths"])
if st.button("Get Formulas"):
    fetch_formulas(selected_subject)
