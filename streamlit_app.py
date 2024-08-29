import streamlit as st

import numpy as np
import pandas as pd
import arxivscraper
import time
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

#files = os.listdir("data")
#option = st.selectbox(
#    "File Available",
#    files,
#)

#col11, col12, col13, col14 = st.columns(4)
#with col11:
#    if st.button("Check this File"):
#        st.session_state.f_name = option
#        st.session_state.df = pd.read_csv("data/{}".format(option))
#        st.session_state.df["status"] = None
#        #st.dataframe(st.session_state.df)
#        st.session_state.read = True

@st.cache_data
def check_then_scrape(category, start, end):
    # get scrape
    time.sleep(3.5)
    scraper = arxivscraper.Scraper(
        category = category, 
        date_from = start,
        date_until = end,
        t = 5)

    # scrape
    output = scraper.scrape()
    
    try:
        # output save
        cols = ('id', 'title', 'categories', 'abstract', 'doi', 'created', 'updated', 'authors')
        df = pd.DataFrame(output, columns=cols)
        return df
    except:
        print(output)
        return output

date = st.text_input("Enter a start Date using YYYY-MM-DD format.")
date1 = st.text_input("Enter an end Date using YYYY-MM-DD format.")
#with col12:
if st.button("Download this Date"):
    st.session_state.f_name = date
    st.session_state.df = check_then_scrape("cs", date, date1)
    st.session_state.df = st.session_state.df[st.session_state.df.created == date]
    st.session_state.df.reset_index(drop = True, inplace = True)
    st.session_state.df["status"] = None
    #st.dataframe(st.session_state.df)
    st.session_state.read = True

if st.session_state.f_name != "":
    csv1 = convert_df(st.session_state.df)
    st.download_button(
                label="Download all papers",
                data=csv1,
                file_name="all_{}".format(st.session_state.f_name),
                mime="text/csv",
            )

    st.dataframe(st.session_state.df)

st.divider()
focus_word = ["large language model", "reinforcement learning", "interpretability", "explainability", "agent", "diffusion"]
except_word = ["autonomous vehicle", "computer vision", "robots"]
if st.session_state.read:
    if st.session_state.idx < len(st.session_state.df):
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
        abs = st.session_state.df.at[st.session_state.idx, "abstract"]
        for fw in focus_word:
            abs = abs.replace(fw, ':red[{}]'.format(fw))
        for fw in except_word:
            abs = abs.replace(fw, ':green[{}]'.format(fw))
        st.markdown("### {}".format(st.session_state.df.at[st.session_state.idx, "title"]))
        st.write("{}".format(abs))
        st.write(st.session_state.df.at[st.session_state.idx, "status"])
    else:
        st.write("Finished Task")
        st.dataframe(st.session_state.df)
        csv = convert_df(st.session_state.df)#[st.session_state.df.status.isin(["R", "I"])])
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name="checked_{}".format(st.session_state.f_name),
            mime="text/csv",
        )