import streamlit as st

from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import numpy as np
import pandas as pd
import arxivscraper
import time
import os

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index = False).encode("utf-8")

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

def send_email(date, df_conv, tmp = False):
    ps = "llwv nrkx znxq spwi"
    # Create the email
    if tmp == True:
        subject = "Tmp Paper Read of {}".format(date)
    else:
        subject = "Paper Read of {}".format(date)
    body = "Sent from PaperDailyRead."

    msg = MIMEMultipart()
    msg['From'] = "hunter.paper.read@gmail.com"
    msg['To'] = "hunter.paper.read@gmail.com"
    msg['Cc'] = "hjiang24@ncsu.edu"
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))

    # File to be attached
    if tmp == True:
        file_path = "tmp_checked_{}".format(st.session_state.f_name)
    else:
        file_path = "checked_{}".format(st.session_state.f_name)
    file_name = os.path.basename(file_path)

    # Create an attachment from the CSV data
    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(df_conv)
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        "attachment; filename={}.csv".format(file_name)
    )

    msg.attach(attachment)

    smtp_server = "smtp.gmail.com"  # e.g., "smtp.gmail.com" for Gmail
    smtp_port = 587  # 587 for TLS, 465 for SSL

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login("hunter.paper.read@gmail.com", ps)
            server.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

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
#date1 = st.text_input("Enter an end Date using YYYY-MM-DD format.")

if date.find("-") > -1:
    initial_date = datetime.strptime(date, "%Y-%m-%d")
    new_date = initial_date + timedelta(days=2)
    date1 = new_date.strftime("%Y-%m-%d")
else:
    date1 = ""

#with col12:
if st.button("Download this Date"):
    st.session_state.f_name = date
    st.session_state.df = check_then_scrape("cs", date, date1)
    #st.session_state.df = st.session_state.df[(st.session_state.df.created == date) | (st.session_state.df.updated == date)]
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
                file_name="all_{}.csv".format(st.session_state.f_name),
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
                #st.session_state.df.to_csv("data_marked/{}".format(st.session_state.f_name))
                csv = convert_df(st.session_state.df)
                st.download_button(
                    label="Download current file as CSV",
                    data=csv,
                    file_name="tmp_checked_{}.csv".format(st.session_state.f_name),
                    mime="text/csv",
                )
                send_email(date, csv, tmp = True)
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
            file_name="checked_{}.csv".format(st.session_state.f_name),
            mime="text/csv",
        )
        send_email(date, csv)