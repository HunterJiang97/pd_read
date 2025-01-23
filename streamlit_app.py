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

if "fw" not in st.session_state:
    st.session_state.fw = [
    "reinforcement learning", 
    "interpretability", 
    "explainability", 
    "agent",
    "time series",
    "survey"
    ]
if "ew" not in st.session_state:
    st.session_state.ew = [
    "autonomous vehicle", 
    "robots",
    "3d",
    "multimodal",
    "graph",
    "pose",
    "segmentation",
    "visual",
    "speech",
    "federated",
    "reconstruction",
    "medical",
    "quantum",
    "differential privacy",
    "5g network",
    "vedio generation",
    "autonomous driving",
    "mri",
    "facial recognition",
    "remote sensor",
    "aerial vehicles",
    "block chain",
    "uav", 
    "asr",
    "vision",
    "editing",
    "smart contract",
    "robot",
    "digital twin",
    "forecasting",
    "graph neural network",
    "point cloud",
    "deep fake",
    "deepfake",
    "super resolution",
    "super-resolution",
    "wearable",
    "spatio-temporal",
    "spatiotemporal",
    "spatio temporal",
    "video"
    ]

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

@st.cache_data
def check_then_scrape(category, start, end):
    print(1)
    # get scrape
    time.sleep(3.5)
    scraper = arxivscraper.Scraper(
        category = category, 
        date_from = start,
        #date_until = end, # put it as today to get recend papers.
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
    print(len(st.session_state.df))
    print(st.session_state.df.head())
    st.session_state.df = st.session_state.df[st.session_state.df.created == date]
    print(len(st.session_state.df))
    st.session_state.df["status"] = None
    st.session_state.read = True
    
    pre_check = []
    for idx, row in st.session_state.df.iterrows():
        flag = True
        for word in st.session_state.ew:
            if row["title"].find(word) > -1:
                flag = False
                break
        
        if not flag:
            for word in st.session_state.fw:
                if row["title"].find(word) > -1:
                    flag = True
                    break
        pre_check.append(int(flag))
    st.session_state.df["flag"] = pre_check
    st.session_state.df = st.session_state.df.sort_values(by = "flag")
    st.session_state.df.reset_index(drop = True, inplace = True)
    st.session_state.df.loc[st.session_state.df.flag == 0, "status"] = "P"
    st.session_state.idx = sum(st.session_state.df.status == "P")
if st.session_state.f_name != "":
    csv1 = convert_df(st.session_state.df)
    st.download_button(
                label="Download all papers",
                data=csv1,
                file_name="all_{}.csv".format(st.session_state.f_name),
                mime="text/csv",
            )

    #st.dataframe(st.session_state.df)

st.divider()
if st.session_state.read:
    my_bar = st.progress(st.session_state.idx / len(st.session_state.df), text= "Read Progress : {} / {}".format(st.session_state.idx, len(st.session_state.df)))
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
                if len(st.session_state.df) > 0:
                    send_email(date, csv, tmp = True)
        if st.session_state.idx < len(st.session_state.df) - 1:
            abs = st.session_state.df.at[st.session_state.idx, "abstract"]
            for fw in st.session_state.fw:
                abs = abs.replace(fw, ':red[{}]'.format(fw))
            for fw in st.session_state.ew:
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
        if len(st.session_state.df) > 0:
            send_email(date, csv)