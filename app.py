import os
import openpyxl
import json
import requests
import streamlit as st
import pandas as pd
import numpy as np
import smtplib
from email.message import EmailMessage
from streamlit_lottie import st_lottie
from st_aggrid import AgGrid
from datetime import datetime
import streamlit.components.v1 as components
import altair as alt

def main_page():
    
    st.title("📊 LinkedIn Engagement Analyzer")
    st.caption("Analyze and optimize your content performance with actionable insights")

    # sidebar
    st.sidebar.markdown("# LinkedIn Engagement Analysis")
    st.sidebar.markdown("**Created by Sumedha Chattree**")
    st.sidebar.markdown("You can **start** by uploading your data on the **LinkedIn Engagement Analysis** page.")
    st.sidebar.markdown("The process for obtaining your data can be found on the **Data Directions and Instructions** page.")

    # main content
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("How engaging are your posts?")
        st.markdown("You can monitor the performance of your posts over time by analyzing their engagements, impressions, and the percentage of engagement per impression.")
        st.markdown("By clicking on any data point, you will be redirected to the link of the corresponding post.")
    with col2:
        def load_lottieurl(url:str):
            r = requests.get(url)
            if r.status_code != 200:
                return None
            return r.json()
        lottie_animation = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_cdu97cbh.json")
        st_lottie(lottie_animation, key="animation")

def page2():
    st.write("# LinkedIn Engagement Analysis")

    # File upload
    file1 = st.sidebar.file_uploader(
        "Upload Engagements & Impressions File",
        type=["xlsx"],
    )

    # ✅ DEMO DATA
    if file1 is None:
        st.info("Using demo dataset. Upload your own file for real analysis.")

        df = pd.DataFrame({
            "Date": pd.date_range(start="2024-01-01", periods=10),
            "Engagements": [10, 20, 15, 30, 25, 40, 35, 50, 45, 60],
            "Impressions": [100, 200, 150, 300, 250, 400, 350, 500, 450, 600]
        })
        df["Date"] = df["Date"].dt.date
    else:
        try:
            df = pd.read_excel(file1)
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
        except Exception as e:
            st.error(f"Error reading file: {e}")
            return

    # Second file
    file2 = st.sidebar.file_uploader(
        "Upload Shares File",
        type=["csv"],
    )

    try:
        if file2 is not None:
            df2 = pd.read_csv(file2)

            df2["DateTime"] = df2["Date"]
            df2["Date"] = pd.to_datetime(df2["Date"]).dt.date
            df2["Time"] = pd.to_datetime(df2["DateTime"]).dt.time
            df2 = df2.rename({'ShareCommentary': 'Post'}, axis=1)

            df = df.merge(df2, on="Date", how="left")

        # Fill missing values
        df["Post"] = df.get("Post", pd.Series(["No post this day."] * len(df)))
        df["ShareLink"] = df.get("ShareLink", pd.Series(["https://www.linkedin.com/feed/"] * len(df)))

    except Exception as e:
        st.warning("Issue processing shares file")

    # Plot settings
    st.sidebar.subheader("Setting the Plot")
    plot_width = st.sidebar.slider("Plot Width", 1, 25, 7)
    plot_height = st.sidebar.slider("Plot Height", 1, 10, 2)

    try:
        min_date = min(df["Date"])
        max_date = max(df["Date"])

        st.markdown("Hover over any point to see details.")

        date_range = st.slider(
            'Select Date Range',
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date)
        )

        df = df[(df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])]

        df["Percent"] = round(
            100 * df["Engagements"].div(df["Impressions"]).replace(np.nan, 0), 2
        )

        source = df

        # Altair chart (your original)
        nearest = alt.selection(type='single', nearest=True, on='mouseover',
                                fields=['Date'], empty='none')

        base = alt.Chart(source).encode(
            alt.X('Date:T', axis=alt.Axis(title=None))
        )

        line1 = base.mark_line().encode(
            alt.Y('Engagements')
        )

        line2 = base.mark_line().encode(
            alt.Y('Impressions')
        )

        chart = alt.layer(line1, line2)

        st.altair_chart(chart, use_container_width=True)

        # Summary stats
        st.subheader("Summary Statistics")
        st.write(df.describe())

        # ✅ INSIGHTS (FIXED)
        st.markdown("##")
        st.subheader("Insights")

        if not df.empty:
            try:
                best_day = df.loc[df["Engagements"].idxmax()]
                st.success(f"Your highest engagement was on {best_day['Date']} with {best_day['Engagements']} engagements.")

                avg_engagement = df["Engagements"].mean()
                st.info(f"Average engagement: {round(avg_engagement, 2)}")

            except Exception as e:
                st.warning("Unable to generate insights.")
        
        # Table
        st.markdown("##")
        st.subheader("Filtered Data Table")
        st.dataframe(df)

    except Exception as e:
        st.error(f"Error generating chart: {e}")
def page3():
    st.write("# LinkedIn Engagement Analysis")

    # Socials Connection
    st.sidebar.title('Connect with me -')

    linkedin_button = '<a href="https://www.linkedin.com/in/sumedhachattree/" target="_blank" style="text-align: center; margin: 0px 10px; padding: 5px 10px; border-radius: 5px; color: white; background-color: #0077B5; text-decoration: none">LinkedIn</a>'
    github_button = '<a href="https://github.com/SumedhaChattree" target="_blank" style="text-align: center; margin: 0px 10px; padding: 5px 10px; border-radius: 5px; color: white; background-color: #24292E; text-decoration: none">GitHub</a>'

    st.sidebar.markdown(f'{linkedin_button} {github_button}', unsafe_allow_html=True)

    # Contact form
    st.sidebar.markdown('Please fill out the form below to contact me.')

    with st.sidebar.form('Contact Form'):
        name = st.text_input('Name')
        email = st.text_input('Email')
        message = st.text_area('Message')
        submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        print(f'Name: {name}')
        print(f'Email: {email}')
        print(f'Message: {message}')
        st.success('Thank you for reaching out! I will get back to you as soon as possible.')

    #Main page
    st.subheader("Download Impressions & Engagements Data")
    st.markdown("This file provides the data necessary for plotting.")
    st.markdown("In order to download the Impressions & Engagements Data follow the following path - Your LinkedIn Profile -> Analytics & tools -> Post Impressions -> Export.")
    st.markdown("**Note:**")
    st.markdown("- After clicking Post Impressions you can edit the timeline for which you want to export the data for and this dashboard can be used with only this file if you choose.")
    st.markdown("- It is optional to upload your Shares file, but you won't be able to click through to posts from the chart.")
    st.subheader("Download Shares Data (Optional)")
    st.markdown("This data is necessary to provide the following:")
    st.markdown("- The previews of your posts' text on the charts when data points are hovered over")
    st.markdown("- The feature to click on any data point and be directed to the post you shared on a particular day")
    st.markdown("You'll have to request an archive of your data from LinkedIn following the instructions at this [link](https://www.linkedin.com/help/linkedin/answer/50191/downloading-your-account-data?lang=en). This generally takes ~24 hours, so go and request that!")
    st.markdown("In the meanwhile, it is possible to experiment with the readily accessible data on Engagements and Lmpressions from and for your LinkedIn Profile. Please refer to the instructions provided above.")

# create site
page_names_to_funcs = {
    "Welcome": main_page,
    "LinkedIn Engagement Analysis": page2,
    "Data Directions and Instructions": page3
}
selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()
