import streamlit as st
import pandas as pd
import json


json_path = r"D:\deeptuned.ai\uiStreamlit\example_data.json"
df = pd.read_json(json_path)

# Save data to a DataFrame
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


# st.write("Subject:", st.session_state.subject)

if st.session_state.start == 1:
    st.write("User:", st.session_state.user)
container = st.container()
with container:
    st.subheader("Before")
    selected_id = "5d817e09-afce-11ee-9384-e2807b4aead7"
    selected_row = df[df['html'] == selected_id]
    st.markdown(selected_row.to_htm, unsafe_allow_html=True)

    st.subheader("After")
    selected_text=df[df['text'] == selected_id]
    st.dataframe(selected_text)

    options = ["Accept", "Reject"]
    option = st.radio("Select an option:", options)
    
    
    if option == "Accept" or option == "Reject":
        comments = st.text_area("Comments:")
        save_button = st.button("Save & Next")

        if save_button:
            st.text("Option Selected: " + option)
            st.text("Comments: " + comments)
            