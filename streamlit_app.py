import streamlit as st

import numpy as np
import pandas as pd

import os

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")

def next_one(mark):
    st.session_state.df.at[st.session_state.idx, "status"] = mark
    st.session_state.idx += 1

if "f_name" not in st.session_state:
    st.session_state.f_name = ""
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()
if "read" not in st.session_state:
    st.session_state.read = False
if "idx" not in st.session_state:
    st.session_state.idx = 0

files = os.listdir("data")
option = st.selectbox(
    "File Available",
    files,
)
if st.button("Check this File"):
    st.session_state.f_name = option
    st.session_state.df = pd.read_csv("data/{}".format(option))
    st.session_state.df["status"] = None
    #st.dataframe(st.session_state.df)
    st.session_state.read = True

st.divider()
if st.session_state.read:
    if st.session_state.idx < len(st.session_state.df):
        st.markdown("### {}".format(st.session_state.df.at[st.session_state.idx, "title"]))
        st.markdown("{}".format(st.session_state.df.at[st.session_state.idx, "abstract"]))
        st.write(st.session_state.df.at[st.session_state.idx, "status"])

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("Pass"):
                next_one("P")
        with col2:
            if st.button("Relavent"):
                next_one("R")
        with col3:
            if st.button("Interested"):
                next_one("I")
        with col4:
            if st.button("Go to last one"):
                st.session_state.idx -= 1
        with col5:
            if st.button("Save"):
                st.session_state.df.to_csv("data_marked/{}".format(st.session_state.f_name))
                csv = convert_df(st.session_state.df)
                st.download_button(
                    label="Download current file as CSV",
                    data=csv,
                    file_name="tmp_checked_{}".format(st.session_state.f_name),
                    mime="text/csv",
                )
    else:
        st.write("Finished Task")
        st.dataframe(st.session_state.df)
        csv = convert_df(st.session_state.df[st.session_state.df.status.isin(["r", "i"])])
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name="checked_{}".format(st.session_state.f_name),
            mime="text/csv",
        )