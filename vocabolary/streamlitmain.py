import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

def extract_tables(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('table')
    return tables

def has_required_fields(table):
    fields = ["Chemical Compound", "Chemical Formula", "Compound Name", "Molecular Formulae"]
    count = 0
    for field in fields:
        if field.lower() in table.get_text().lower():
            count += 1
    return count >= 2

def extract_table_text(tables):
    table_text = ""
    serial_number = 1
    for table in tables:
        if has_required_fields(table):
            rows = table.find_all('tr')
            header_cells = rows[0].find_all(['th', 'td'])
            sl_no_column_index = -1
            for idx, cell in enumerate(header_cells):
                if cell.get_text(strip=True).lower() == "sl. no":
                    sl_no_column_index = idx
                    break
            for row in rows[1:]:
                cells = row.find_all(['th', 'td'])
                row_text = f"{serial_number}. "
                serial_number += 1
                for idx, cell in enumerate(cells):
                    if idx == sl_no_column_index:
                        continue
                    cell_text = cell.get_text(strip=True)
                    cell_text = cell_text.lstrip('0123456789')
                    row_text += f"{cell_text.strip()} "
                if row_text:
                    table_text += f"{row_text}\n"
    return table_text

def fetch_formulas(subject):
    if subject == "Physics":
        url = "https://www.pw.live/exams/school/physics-formulas/"
        display_style = "list"
    elif subject == "Chemistry":
        url = "https://en.wikipedia.org/wiki/Glossary_of_chemical_formulae"
        display_style = "table"
    elif subject == "Maths":
        url = "https://www.pw.live/exams/school/math-formulas/"
        display_style = "list"
    else:
        st.error("Invalid subject selected.")
        return

    response = requests.get(url)
    if response.status_code == 200:
        if display_style == "table":
            tables = extract_tables(url)
            if tables:
                st.markdown("**Formulas:**")
                table_text = extract_table_text(tables)
                lines = table_text.split('\n')
                for line in lines:
                    st.markdown(f"<p style='font-size: 18px; margin-bottom: 5px;'><b>{line}</b></p>", unsafe_allow_html=True)
        elif display_style == "list":
            soup = BeautifulSoup(response.content, 'html.parser')
            pattern = re.compile(r".*=.*")
            list_items = soup.find_all('li', string=pattern)
            st.markdown("**Formulas:**")
            for idx, li in enumerate(list_items, start=1):
                st.markdown(f"<p style='font-size: 18px; margin-bottom: 5px;'><b>{idx}. {li.get_text()}</b></p>", unsafe_allow_html=True)
    else:
        st.error("Failed to retrieve the webpages")

st.title("Formula Dictionary")
selected_subject = st.selectbox("Select a Subject", ["Physics", "Chemistry", "Maths"])
if st.button("Get Formulas"):
    fetch_formulas(selected_subject)