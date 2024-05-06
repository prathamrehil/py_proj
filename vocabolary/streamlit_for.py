import streamlit as st
import re
from io import StringIO

# Function to process LaTeX expressions from an uploaded file
def process_latex_from_file(uploaded_file):
    latex_expressions = []
    file_contents = uploaded_file.getvalue().decode("utf-8")
    lines = file_contents.split("\n")
    for line in lines:
        # Extract LaTeX expressions using regular expression
        latex_matches = re.findall(r'\$(.*?)\$', line)
        if latex_matches:
            latex_expressions.extend(latex_matches)
    return latex_expressions

# Rest of your code remains the same...


# Function to render LaTeX expressions using MathJax
def render_latex(latex_expressions):
    for idx, latex_expr in enumerate(latex_expressions):
        st.write(f"**LaTeX Expression {idx + 1}:**")
        st.markdown(f"```latex\n{latex_expr}\n```")
        st.markdown(f"$$ {latex_expr} $$", unsafe_allow_html=True)

def main():
    st.title("LaTeX Expression Viewer")

    # File uploader for uploading text files
    uploaded_file = st.file_uploader("Upload a text file", type=["txt"])

    if uploaded_file is not None:
        # Read and process LaTeX expressions from the uploaded file
        latex_expressions = process_latex_from_file(uploaded_file)

        # Render LaTeX expressions
        if latex_expressions:
            render_latex(latex_expressions)
        else:
            st.write("No LaTeX expressions found in the file.")

if __name__ == "__main__":
    main()
