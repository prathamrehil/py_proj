from pymongo import MongoClient
import streamlit as st
import re

def unprocess(text):
    return re.sub(r"\$[^$]*\$", "", text, flags=re.MULTILINE)

def wrap_html(html):
    styles = """
<style>
body {
    text-align: left;
}

.container {
    padding: 10px;
    border: 1px solid grey;
}

img {
    border: 1px solid red;
}
</style>
"""
    return f'{styles}\n\n<div class="container">{html}</div>'

client = MongoClient('localhost', 27017)
db = client['example_data']  

if "i" not in st.session_state:
    st.session_state.i = 0	
if "start" not in st.session_state or "user" not in st.session_state or "subject" not in st.session_state:
    st.session_state.start = None
    st.session_state.user = ""
    st.session_state.subject = ""

if st.session_state.start is None:
    st.title("Login with your email")
    sample_emails = ["user1@example.com", "user2@example.com", "user3@example.com"]
    email = st.selectbox("Select your email:", sample_emails)
    subjects = ["Physics", "Chemistry", "Maths", "Zoology", "Botany"]
    selected_subject = st.selectbox("Select a subject:", subjects)
    start_button = st.button("Start")

    if start_button:
        st.session_state.start = 1
        st.session_state.user = email
        st.session_state.subject = selected_subject
        st.write("User:", st.session_state.user)
        st.write("Subject:", st.session_state.subject)
        st.rerun()

# Existing code...
if st.session_state.start == 1:
    st.write("User:", st.session_state.user)
    st.write("Subject:", st.session_state.subject)
    if st.session_state.subject == "Physics":
        collection = db['physics'] 
    elif st.session_state.subject == "Chemistry":
        collection = db['chemistry'] 
    elif st.session_state.subject == "Maths":
        collection = db['maths'] 
    elif st.session_state.subject == "Zoology":
        collection = db['zoology'] 
    elif st.session_state.subject == "Botany":
        collection = db['botany'] 
    documents = list(collection.find())  # Convert cursor to list

    if st.session_state.i < len(documents):  # Check if there are more documents
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Before")
            col1._html(wrap_html(documents[st.session_state.i]['html']), height=300, scrolling=True)
        with col2:
            st.subheader("After")
            ct = st.container(border=True)
            ct.write(unprocess(documents[st.session_state.i]['text']))
        options = ["Accept", "Reject"]
        option = st.radio("Select an option:", options)
        if option :
            comments = st.text_area("Comments:")
            save_button = st.button("Save & Next")
            if save_button:
                dic = {
                    "user": st.session_state.user,
                    "subject": st.session_state.subject,
                    "question_id": documents[st.session_state.i]['question_id'],
                    "option": option,
                    "comments": comments
                }
                collect = db['review']
                st.session_state.i += 1
                insert_result = collect.insert_one(dic)
                st.rerun()
    else:
        st.write("No more documents to review.")