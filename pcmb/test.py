import streamlit as st
import re, json
import numpy as np
import pandas as pd
import re
from sequence_handler import get_html, align_sequence, get_markdown

st.set_page_config(layout="wide")

def get_difference_html(s1, s2):
    alignment = align_sequence(s1, s2)
    return get_html(alignment.first, alignment.second)
def get_difference_text(s1, s2):
    alignment = align_sequence(s1, s2)
    return get_markdown(alignment.first, alignment.second)

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


def data_path(start, subject):
    path = ""
    if subject == "Maths":
        path = f"maths_data_html_correction.csv"
        df = pd.read_csv(path)
        df_new = df[df["marked_for_review"] == 1]

    elif subject == "Physics":
        path = "physics_data_html_correction.csv"
        df = pd.read_csv(path)
        df_new = df[df["marked_for_review"] == 1]
    elif subject == "Chemistry":
        path = "chem_data_html_correction.csv"
        df = pd.read_csv(path)
        df_new = df[df["marked_for_review"] == 1]
    elif subject == "Biology":
        path = "bio_data_html_correction.csv"
        df = pd.read_csv(path)
        df_new = df[df["marked_for_review"] == 1]
    if start == 1 or start == 3:
        return df, path
    elif start == 2:
        return df, df_new, path


def display_text_or_html(batch, i, j, display):
    col1, col2, col4 = st.columns(3)
    if display == "text":
        with col1:
            st.subheader("allen Question")
            col1.write(wrap_html(batch["html"].iloc[i]), unsafe_allow_html=True)

        with col2:
            st.subheader(f"Induced Error Html {i + j+1}")
            # col2.write(
            #         wrap_html(get_difference_html(batch["html"].iloc[i], batch["error_induced_html"].iloc[i])), unsafe_allow_html=True
            # )
            col2.write(wrap_html(batch["error_induced_html"].iloc[i]), unsafe_allow_html=True)

        with col3:
            st.subheader("Induced Error Text")
            ct = st.container()
            ct.write(batch["error_induced_text"].iloc[i])

        with col4:
            st.subheader("Gpt Corrected")
            ct = st.container()
            ct.write(batch["error_corrected_text"].iloc[i])
    if display == "html":
        with col1:
            st.subheader("allen Question")
            col1.write(wrap_html(batch["html"].iloc[i]), unsafe_allow_html=True)
        with col2:
            st.subheader("Induced Error")
            ct = st.container()
            col2.write(
                wrap_html(batch["error_induced_html"].iloc[i]), unsafe_allow_html=True
            )

        with col4:
            st.subheader("Gpt Corrected")
            ct = st.container()
            ct.write(
                wrap_html(batch["error_corrected_html"].iloc[i]), unsafe_allow_html=True
            )


if "start" not in st.session_state or "subject" not in st.session_state:
    st.session_state.start = 0
    st.session_state.subject = ""
if "data" not in st.session_state:
    st.session_state["data"] = None
if "error" not in st.session_state:
    st.session_state.error = 0
if "display" not in st.session_state:
    st.session_state.display = ""

if st.session_state.start == 0:
    Modes = ["Find Errors", "Show Errors", "Search"]
    mode = st.selectbox("Select Mode:", Modes)
    subjects = ["Physics", "Chemistry", "Maths", "Biology"]
    selected_subject = st.selectbox("Select a subject:", subjects)
    dis = ["text", "html"]
    display = st.selectbox("Select Display:", dis)
    start_button = st.button("Start")
    if start_button:
        if mode == "Find Errors":
            st.session_state.start = 1
        if mode == "Show Errors":
            st.session_state.start = 2
        if mode == "Search":
            st.session_state.start = 3
        st.session_state.subject = selected_subject
        st.session_state.display = display
        st.rerun()

if st.session_state.start == 1 or st.session_state.start == 2:
    path = ""
    df = None
    if st.session_state.start == 1:
        st.session_state["data"], path = data_path(
            st.session_state.start, st.session_state.subject
        )
    elif st.session_state.start == 2:
        df, st.session_state["data"], path = data_path(
            st.session_state.start, st.session_state.subject
        )
    SAMPLE_SIZE = (
        10 if len(st.session_state["data"]) > 10 else len(st.session_state["data"])
    )

    if "i" not in st.session_state:
        st.session_state["i"] = 0
    if "j" not in st.session_state:
        st.session_state.j = 0
    if "remarks" not in st.session_state:
        st.session_state.remarks = []

    if "batch" not in st.session_state:
        st.session_state["batch"] = st.session_state["data"][
            st.session_state["i"]
            * SAMPLE_SIZE : (st.session_state["i"] + 1)
            * SAMPLE_SIZE
        ]

    st.session_state["batch"] = st.session_state["data"].iloc[
        st.session_state["i"] * SAMPLE_SIZE : (st.session_state["i"] + 1) * SAMPLE_SIZE
    ]

    st.title("Reviewing")

    col1, col2, col3 = st.columns(3)
    with col1:
        lis = [i * 10 for i in range(len(st.session_state["data"]) // 10)]
        options = st.selectbox("Select Batch:", lis)
        if st.button("Move to"):
            st.session_state["i"] = int(options / 10)
            st.session_state.j = int(st.session_state["i"] * 10)
            st.rerun()
    with col2:
        subjects = ["Physics", "Chemistry", "Maths", "Biology"]
        option_subject = st.selectbox(
            "Select Subject:", subjects, index=subjects.index(st.session_state.subject)
        )
        if st.button("Change"):
            st.session_state.subject = option_subject
            st.session_state["data"], path = data_path(
                st.session_state.start, st.session_state.subject
            )
            st.session_state["i"] = 0
            st.session_state.j = 0
            st.rerun()
    with col3:
        number_of_errors = len(
            st.session_state["data"][st.session_state["data"]["marked_for_review"] == 1]
        )
        st.write(f"Number of errors: {number_of_errors}")

    for i in range(len(st.session_state["batch"])):
        q_container = st.container(border=True)
        with q_container:
            display_text_or_html(
                st.session_state["batch"],
                i,
                st.session_state.j,
                st.session_state.display,
            )

            with st.form(key=f"form{i}", clear_on_submit=True):
                col5, col6 = st.columns(2)

                with col5:
                    if (
                        st.session_state["data"][
                            st.session_state["batch"].iloc[i]["question_id"]
                            == st.session_state["data"]["question_id"]
                        ].iloc[0]["marked_for_review"]
                        == 1
                    ):
                        st.error("Flagged")
                    st.container(border=False).write(
                        f"<small>{st.session_state['batch'].iloc[i]['question_id']}</small>",
                        unsafe_allow_html=True,
                    )
                    save = st.form_submit_button("Save")
                with col6:
                    common_remarks = [
                        "Img or text spacing changed",
        "Missing or editing option",
        "image src link changed: No image rendered",
        "HTML tags changed: to latex/normal text",
        "Missing or omitted words",
        "Allen tags issue",
        "Singular : Plural issue",
        "Image tag removed",
        "Symbols changed",
        "Answered the question" 
                    ]
                    # col_name = tag.lower().replace(" ", "_")
                    unique_remarks = st.multiselect("Select Remark:", common_remarks)

                    r = st.session_state["data"][
                        st.session_state["batch"].iloc[i]["question_id"]
                        == st.session_state["data"]["question_id"]
                    ].iloc[0]["remarks"]
                    if pd.notna(r) and r != "":
                        remarks = st.text_input(label="Remarks", value=f"{r}")
                    else:
                        remarks = st.text_input(label="Remarks", value=f"")

                    if save:
                        if st.session_state.start == 1:
                            st.session_state["data"].loc[
                                st.session_state["batch"].iloc[i]["question_id"]
                                == st.session_state["data"]["question_id"],
                                "marked_for_review",
                            ] = 1
                            for remark in unique_remarks:
                                tag = remark.lower().replace(" ", "_")
                                st.session_state["data"].loc[
                                    st.session_state["batch"].iloc[i]["question_id"]
                                    == st.session_state["data"]["question_id"],
                                    tag,
                                ] = True
                            st.session_state["data"].loc[st.session_state["batch"].iloc[i]["question_id"]
                                == st.session_state["data"]["question_id"], "remarks"] = remarks
                            st.session_state["data"].to_csv(path, index=False)
                            st.rerun()
                        elif st.session_state.start == 2:
                            df.loc[
                                st.session_state["batch"].iloc[i]["question_id"]
                                == df["question_id"],
                                "marked_for_review",
                            ] = 1
                            for remark in unique_remarks:
                                tag = remark.lower().replace(" ", "_")
                                df.loc[
                                    st.session_state["batch"].iloc[i]["question_id"]
                                    == df["question_id"],
                                    tag,
                                ] = True
                            df.loc[st.session_state["batch"].iloc[i]["question_id"], "remarks"] = remarks
                            df.to_csv(path, index=False)
                            st.rerun()
            col7, col8 = st.columns(2)
            with col7:
                clear = st.button("Clear", key=f"clear{i}")
                if clear:
                    st.session_state["data"].loc[
                        st.session_state["batch"].iloc[i]["question_id"]
                        == st.session_state["data"]["question_id"],
                        "marked_for_review",
                    ] = 0
                    st.session_state["data"].loc[
                        st.session_state["batch"].iloc[i]["question_id"]
                        == st.session_state["data"]["question_id"],
                        "remarks",
                    ] = ""
                    for remark in common_remarks:
                        tag = remark.lower().replace(" ", "_")
                        st.session_state["data"].loc[
                            st.session_state["batch"].iloc[i]["question_id"]
                            == st.session_state["data"]["question_id"],
                            tag,
                        ] = False
                    st.session_state["data"].to_csv(path, index=False)
                    st.rerun()
            with col8:
                with st.expander("View raw content"):
                    st.markdown("<h5>HTML</h5>", unsafe_allow_html=True)
                    st.code(st.session_state["batch"]["html"].iloc[i], language="html")
                    st.write("---------------------------------------------------")
                    st.markdown("<h5>Error Induced HTML</h5>", unsafe_allow_html=True)
                    st.code(st.session_state["batch"]["error_induced_html"].iloc[i], language="html")
                    st.write("---------------------------------------------------")
                    st.markdown("<h5>Error Induced Text</h5>", unsafe_allow_html=True)
                    st.code(
                        st.session_state["batch"]["error_induced_html"].iloc[i],
                        language="html",
                    )
                    st.write("---------------------------------------------------")
                    st.markdown("<h5>Error Corrected Text</h5>", unsafe_allow_html=True)
                    st.code(
                        st.session_state["batch"]["error_corrected_html"].iloc[i],
                        language="html",
                    )


    col8, col9 = st.columns(2)
    with col8:
        if st.button("back"):
            st.session_state["i"] -= 1
            st.session_state.j -= 10
            st.rerun()
    with col9:
        if st.button("Next sample"):
            st.session_state["i"] += 1
            st.session_state["j"] += 10
            st.rerun()
if st.session_state.start == 3:
    filtered_df = None
    search = st.text_input("Search")
    df, path = data_path(st.session_state.start, st.session_state.subject)
    if st.button("Search"):
        search_terms = search.split()
        filtered_df = df[df["question_id"].isin(search_terms)]

        for index, row in filtered_df.iterrows():
            q_container = st.container(border=True)
            with q_container:
                col0, col1, col2, col3 = st.columns(4)
                with col0:
                    st.container(border=True)._html(row["html"], height=400)

                with col1:
                    st.container(border=True).write(row["error_induced_text"])

                with col2:
                    st.container(border=True).write(row["error_induced_text"])

                with col3:
                    st.container(border=True).write(row["error_corrected_text"])

            with st.form(key=f"form{index}", clear_on_submit=True):
                col4, col5 = st.columns(2)
                with col4:
                    if row["marked_for_review"]:
                        st.error("Flagged")
                        st.markdown(
                            f"<small>{row['question_id']}</small>",
                            unsafe_allow_html=True,
                        )
                    flag = st.form_submit_button("Save")
                with col5:
                    remarks = st.text_area(label="Remarks", value=f"{row['remarks']}")
