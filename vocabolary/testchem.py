import requests
import streamlit as st
from bs4 import BeautifulSoup

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
