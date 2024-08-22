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
    #st.dataframe(st.session_state.df)
    st.session_state.read = True

st.divider()
if st.session_state.read:
    if st.session_state.idx < 10:#len(st.session_state.df):
        st.markdown("### {}".format(st.session_state.df.at[st.session_state.idx, "title"]))
        st.markdown("{}".format(st.session_state.df.at[st.session_state.idx, "abstract"]))

        if st.button("Pass"):
            next_one("P")
        if st.button("Relavent"):
            next_one("R")
        if st.button("Interested"):
            next_one("I")
        if st.button("Save"):
            st.session_state.df.to_csv("data_marked/{}".format(st.session_state.f_name))
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