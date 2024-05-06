import streamlit as st
import re, json
import numpy as np
import pandas as pd
import re

st.set_page_config(layout="wide")



def dis_stats(common_remarks):
    errors =len(st.session_state.data[st.session_state.data["marked_for_review"] == 1])
    n_remarks =len(st.session_state.data[st.session_state.data["remarks"] != "False"])
    stats = {"Number of Errors": errors
            ,"Number of Remarks": n_remarks}
    for remark in common_remarks:
        tag = remark.lower().replace(" ", "_")
        stats.update({remark: len(st.session_state.data[st.session_state.data[tag] == True])})
    st.data_editor(stats, height=490,width=300, key="stats")

if "i" not in st.session_state:
    st.session_state.i = 0
if "path" not in st.session_state:
    st.session_state.path = ""
if "data" not in st.session_state:
    st.session_state.data = None

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


st.session_state.path = "18-04-labelled-final.csv"
# st.session_state.path = "data/problem5.csv"
    
st.session_state.data =pd.read_csv(st.session_state.path)


SAMPLE_SIZE = (
        5 if len(st.session_state.data) > 5 else len(st.session_state.data)
    )

if "j" not in st.session_state:
    st.session_state.j = 0
if "remarks" not in st.session_state:
    st.session_state.remarks = []

if "batch" not in st.session_state:
    st.session_state.batch = st.session_state.data[
        st.session_state.i
        * SAMPLE_SIZE : (st.session_state.i + 1)
        * SAMPLE_SIZE
    ]
st.session_state.batch = st.session_state.data[
        st.session_state.i
        * SAMPLE_SIZE : (st.session_state.i + 1)
        * SAMPLE_SIZE
    ]
tag1, tag2= st.tabs(["Labelled","Raw Data"])
lis = [i * 5 for i in range(len(st.session_state.data) // 5)]
options = st.sidebar.selectbox("Select Batch:", lis)
if st.sidebar.button("Move to"):
    st.session_state.i = int(options / 5)
    st.session_state.j = int(st.session_state.i * 5)
    st.rerun()
# with tag2:
#     common_remarks = ["Allen Issue", "Gpt Issue"]
#     dis_stats(common_remarks)
with tag1:
    for i in range(len(st.session_state.batch)):
            q_container = st.container(border=True)
            with q_container:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(f"Question {i + st.session_state.j+1}")
                    col1._html(wrap_html(st.session_state.batch["processed_html"].iloc[i]), height=300, scrolling=True)

                
                # with col2:
                #     st.subheader("After Labelled")
                #     col2._html(wrap_html(st.session_state.batch["Updated_processed_html"].iloc[i]), height=300, scrolling=True)
                #     # col2._html(wrap_html(st.session_state.batch["processed_html"].iloc[i]), height=300, scrolling=True)

with tag2:
    for i in range(len(st.session_state.batch)):
            q_container = st.container(border=True)
            with q_container:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(f"Raw allen Question {i+ st.session_state.j+1}")
                    col1._html(wrap_html(st.session_state.batch["processed_html"].iloc[i]), height=300, scrolling=True)
                
                with col2:
                    st.subheader("After Labelled")
                    k = st.session_state.batch["processed_html"].iloc[i]
                    with st.form(key=f"form{i}", clear_on_submit=True):
                        update = st.text_area("After Labelled", value=k, height=300)
                        col5, col6 = st.columns(2)
                        with col5:
                            # if (
                            #     st.session_state.data[
                            #         st.session_state.batch.iloc[i]["original_row_id"]
                            #         == st.session_state.data["original_row_id"]
                            #     ].iloc[0]["marked_for_review"]
                            #     == 1
                            # ):
                            #     st.error("Flagged")
                            # st.container(border=False).write(
                            #     f"<small>{st.session_state['batch'].iloc[i]['original_row_id']}</small>",
                            #     unsafe_allow_html=True,
                            # )
                            save = st.form_submit_button("Save")
                    with col6:
                        common_remarks = ["Allen Issue", "Gpt Issue"]
                        unique_remarks = st.multiselect("Select Remark:", common_remarks)
                        # r = st.session_state.data[
                        #     st.session_state.batch.iloc[i]["original_row_id"]
                        #     == st.session_state.data["original_row_id"]
                        # ].iloc[0]["remarks"]
                        # if pd.notna(r) and r != "":
                        #     remarks = st.text_input(label="Remarks", value=f"{r}")
                        # else:
                        #     remarks = st.text_input(label="Remarks", value=f"")

                        if save:
                        
                            st.session_state.data.loc[
                                st.session_state.batch.iloc[i]["original_row_id"]
                                == st.session_state.data["original_row_id"],
                                "processed_html",
                            ] = update
                            # for remark in unique_remarks:
                            #     tag = remark.lower().replace(" ", "_")
                            #     st.session_state.data.loc[
                            #         st.session_state.batch.iloc[i]["original_row_id"]
                            #         == st.session_state.data["original_row_id"],
                            #         tag,
                            #     ] = True
                            # st.session_state.data.loc[st.session_state.batch.iloc[i]["original_row_id"]
                            #     == st.session_state.data["original_row_id"], "remarks"] = remarks
                            st.session_state.data.to_csv(st.session_state.path, index=False)
                            st.rerun()
                                
                # col7, col8 = st.columns(2)
                # with col7:
                #     clear = st.button("Clear", key=f"clear{i}")
                #     if clear:
                #         st.session_state.data.loc[
                #             st.session_state.batch.iloc[i]["original_row_id"]
                #             == st.session_state.data["original_row_id"],
                #             "marked_for_review",
                #         ] = 0
                #         st.session_state.data.loc[
                #             st.session_state.batch.iloc[i]["original_row_id"]
                #             == st.session_state.data["original_row_id"],
                #             "remarks",
                #         ] = ""
                #         for remark in common_remarks:
                #             tag = remark.lower().replace(" ", "_")
                #             st.session_state.data.loc[
                #                 st.session_state.batch.iloc[i]["original_row_id"]
                #                 == st.session_state.data["original_row_id"],
                #                 tag,
                #             ] = False
                #         st.session_state.data.to_csv(st.session_state.path, index=False)
                #         st.rerun()
col8, col9 = st.columns(2)
with col8:
    if st.button("back"):
        st.session_state.i -= 1
        st.session_state.j -= 5
        st.rerun()
with col9:
    if st.button("Next sample"):
        st.session_state.i += 1
        st.session_state.j += 5
        st.rerun()

