import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

def fetch_chemical_formulas():
    url = "https://en.wikipedia.org/wiki/Glossary_of_chemical_formulae"
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.find_all("table")

    table_found = False
    for table in tables:
        if any("Chemical formula" in cell.get_text(strip=True) for cell in table.find_all("th")):
            table_found = True
            rows = table.find_all("tr")
            header_row = rows[0].find_all("th")
            cas_index = None
            for i, cell in enumerate(header_row):
                if "CAS" in cell.get_text(strip=True):
                    cas_index = i
                    break
            if cas_index is not None:
                for row in rows:
                    cells = row.find_all(["td", "th"])
                    if len(cells) > cas_index:
                        cells.pop(cas_index)
                    try:
                        row.clear()
                    except AttributeError:
                        pass
                    row.extend(cells)
                    for cell in cells:
                        cell_text = cell.get_text(strip=True)
                        if "Chemical formula" in cell_text or "Synonyms" in cell_text:
                            row.extract()
            st.markdown(str(table), unsafe_allow_html=True)

    if not table_found:
        st.write("Table not found!")


def fetch_formulas(subject):
    if subject == "Physics":
        url = "https://www.pw.live/exams/school/physics-formulas/"
        display_style = "list"
    elif subject == "Chemistry":
        fetch_chemical_formulas()
        return
    elif subject == "Maths":
        url = "https://www.pw.live/exams/school/math-formulas/"
        display_style = "list"
    else:
        st.error("Invalid subject selected.")
        return

    response = requests.get(url)
    if response.status_code == 200:
        if display_style == "list":
            soup = BeautifulSoup(response.content, 'html.parser')
            pattern = re.compile(r".*=.*")
            list_items = soup.find_all('li', string=pattern)
            st.markdown("**Formulas:**")
            for idx, li in enumerate(list_items, start=1):
                st.markdown(f"{idx} $ { li.get_text() } $" , unsafe_allow_html=True)
    else:
        st.error("Failed to retrieve the webpage")

st.title("Formula Dictionary")
selected_subject = st.selectbox("Select a Subject", ["Physics", "Chemistry", "Maths"])
if st.button("Get Formulas"):
    fetch_formulas(selected_subject)
