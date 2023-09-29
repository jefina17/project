import pandas as pd
import streamlit as st
import mysql.connector
import pymongo
from pymongo import MongoClient
from googleapiclient.discovery import build
import streamlit as st

st.title(":red[Youtube Data Harvesting and Warehousing]")
# Define emojis for each option
emojis = {
     "Starting Point": "🌈",
    "Data Gathering & MySQL Data Migration": "🔄",
    "SQL Query": "📊"
}

# Display a dropdown menu with emojis for navigation options
selected_option = st.selectbox("Your Decision 🤔",
                               [f"{emoji} {option}" for option, emoji in emojis.items()])

# Extract the selected option
selected = selected_option.split(' ', 1)[1]

# Display a creative message based on the selected option
if selected == "Home":
    st.write("You've selected the Home option! Welcome to the YouTube Data Harvesting and Warehousing hub.")
elif selected == "Get Data & Transform":
    st.write("You've selected the Get Data & Transform option! Let's gather and process some data.")
elif selected == "SQL Query":
    st.write("You've selected the SQL Query option! Time to query some data.")



# Bridging a connection with MongoDB  and Creating a new database(youtube)
client = pymongo.MongoClient("mongodb+srv://jefinavincy02:jefina1717@cluster0.wz2d2at.mongodb.net/?retryWrites=true&w=majority")

db = client.youtube_jefina

# CONNECTING WITH MYSQL DATABASE
mydb = mysql.connector.connect(host="localhost",
                               user="root",
                               password="Jefina2002",
                               database="youtube_jefi"
                               )
mycursor = mydb.cursor(buffered=True)

# BUILDING CONNECTION WITH YOUTUBE API
api_key = 'AIzaSyCDwVZwBtW7nVAmAgiii1Bwn3wPlYi7q_w'
youtube = build('youtube', 'v3', developerKey=api_key)


# FUNCTION TO GET CHANNEL DETAILS
def get_channel_details(channel_id):
    ch_data = []
    response = youtube.channels().list(part='snippet,contentDetails,statistics',
                                       id=channel_id).execute()

    for i in range(len(response['items'])):
        data = dict(Channel_id=channel_id[i],
                    Channel_name=response['items'][i]['snippet']['title'],
                    Playlist_id=response['items'][i]['contentDetails']['relatedPlaylists']['uploads'],
                    Subscribers=response['items'][i]['statistics']['subscriberCount'],
                    Views=response['items'][i]['statistics']['viewCount'],
                    Total_videos=response['items'][i]['statistics']['videoCount'],
                    Description=response['items'][i]['snippet']['description'],
                    Country=response['items'][i]['snippet'].get('country')
                    )
        ch_data.append(data)
    return ch_data


# FUNCTION TO GET VIDEO IDS
def get_channel_videos(channel_id):
    video_ids = []
    # get Uploads playlist id
    res = youtube.channels().list(id=channel_id,
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None

    while True:
        res = youtube.playlistItems().list(playlistId=playlist_id,
                                           part='snippet',
                                           maxResults=50,
                                           pageToken=next_page_token).execute()

        for i in range(len(res['items'])):
            video_ids.append(res['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')

        if next_page_token is None:
            break
    return video_ids


# FUNCTION TO GET VIDEO DETAILS
import re
from datetime import datetime
import isodate

def get_video_details(v_ids):
    video_stats = []

    for i in range(0, len(v_ids), 50):
        response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(v_ids[i:i + 50])).execute()
        for video in response['items']:
            # Extract minutes and seconds from the ISO 8601 duration using regex
            duration_iso = video['contentDetails']['duration']
            match = re.match(r'PT(\d+)M(\d+)S', duration_iso)
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                duration_seconds = minutes * 60 + seconds
            else:
                duration_seconds = None  # Handle invalid duration format gracefully

            # Convert published date to a Pandas datetime object
            published_date_iso = video['snippet']['publishedAt']
            try:
                published_date = pd.to_datetime(published_date_iso, format='%Y-%m-%dT%H:%M:%SZ')
            except pd.errors.OutOfBoundsDatetime:
                # Handle any invalid date formats or other errors here
                # For example, you can replace invalid dates with NaT (Not-a-Time)
                published_date = pd.NaT

            video_details = dict(
                Channel_name=video['snippet']['channelTitle'],
                Channel_id=video['snippet']['channelId'],
                Video_id=video['id'],
                Title=video['snippet']['title'],
                Thumbnail=video['snippet']['thumbnails']['default']['url'],
                Description=video['snippet']['description'],
                Published_date=published_date,
                Duration_seconds=duration_seconds,
                Views=video['statistics']['viewCount'],
                Likes=video['statistics'].get('likeCount'),
                Comments=video['statistics'].get('commentCount'),
                Favorite_count=video['statistics']['favoriteCount'],
                Definition=video['contentDetails']['definition'],
                Caption_status=video['contentDetails']['caption']
            )
            video_stats.append(video_details)
    return video_stats


# FUNCTION TO GET COMMENT DETAILS
def get_comments_details(v_id):
    comment_data = []
    for i in v_id:
        try:
            response = youtube.commentThreads().list(part="snippet,replies",
                                                     videoId=i,
                                                     maxResults=100).execute()
            for cmt in response['items']:
                data = dict(Comment_id=cmt['id'],
                            Video_id=cmt['snippet']['videoId'],
                            Comment_text=cmt['snippet']['topLevelComment']['snippet']['textDisplay'],
                            Comment_author=cmt['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            Comment_posted_date=cmt['snippet']['topLevelComment']['snippet']['publishedAt'],
                            Like_count=cmt['snippet']['topLevelComment']['snippet']['likeCount'],
                            Reply_count=cmt['snippet']['totalReplyCount']
                            )
                comment_data.append(data)
        except:
            pass
    return comment_data
# FUNCTION TO GET CHANNEL NAMES FROM MONGODB
def channel_names():
    ch_name = []
    for i in db.channel_details.find():
        ch_name.append(i['Channel_name'])
    return ch_name


# HOME PAGE
if selected == "Starting Point":
   st.image("https://www.logo.wine/a/logo/YouTube/YouTube-Icon-Full-Color-Logo.wine.svg", caption="YouTube Logo", width=100)

   # Domain information
   st.markdown("## Specialty 🌠 : <span style='color:blue'> Networld 🌍</span>", unsafe_allow_html=True)
   st.write("<p style='font-size: 24px;'>This app is related to NetWorld🌍</p>", unsafe_allow_html=True)


# Technologies used
   st.markdown("## CodeCraft Kit 🛠️💻:")
   st.write("<p style='font-size: 24px;'>The technologies used in this project include Python, MongoDB, Youtube Data API, MySql, and Streamlit.</p>", unsafe_allow_html=True)


# Overview
   st.markdown("## Helicopter View 🚁:")
   st.write("<p style='font-size: 24px;'>The project involves retrieving Youtube channels' data from the Google API, storing it in a MongoDB as a data lake, migrating and transforming the data into a SQL database, and then querying the data and displaying it in the Streamlit app.</p>", unsafe_allow_html=True)

    # EXTRACT AND TRANSFORM PAGE
if selected == "Data Gathering & MySQL Data Migration":
    tab1, tab2 = st.tabs(["Data Gathering 👉", "MySQL Data Migration 👉"])

    # GET DATA TAB
    with tab1:
        st.markdown("#    ")
        st.write("### 🚀 Unlock Your YouTube Channel Insights: ")
        ch_id = st.text_input("Enter Channel IDs")


        if ch_id and st.button("Extract Data"):
            ch_details = get_channel_details(ch_id)
            st.write(f'#### Extracted data from :green["{ch_details[0]["Channel_name"]}"] channel')
            st.table(ch_details)

        if st.button("Data Sendoff to MongoDB  👉"):
            smiley_emoji = "😊"
            with st.spinner(f'{smiley_emoji} Loading Data {smiley_emoji}'):
                ch_details = get_channel_details(ch_id)
                v_ids = get_channel_videos(ch_id)
                vid_details = get_video_details(v_ids)
                comm_details = get_comments_details(v_ids)

                

                collections1 = db.channel_details
                collections1.insert_many(ch_details)

                collections2 = db.video_details
                collections2.insert_many(vid_details)

                collections3 = db.comments_details
                collections3.insert_many(comm_details)
                st.success("Data Sent to MongoDB Successfully Mission Accomplished !!🎉 ")
                

                # TRANSFORM TAB
    with tab2:
        st.markdown("#   ")
        st.markdown("### Select a channel to begin Transformation to SQL")

        ch_names = channel_names()
        user_inp = st.selectbox("Select channel", options=ch_names)
        

        def table_exists(table_name):
            # Check if the table exists
            mycursor.execute("SHOW TABLES LIKE %s", (table_name,))
            return mycursor.fetchone() is not None

        def create_table(table_name, create_query):
            # Create a table if it doesn't exist
            if not table_exists(table_name):
                mycursor.execute(create_query)
                print(f"Table '{table_name}' created.")

        # Create channel_details table
        channel_details_query = (
            "CREATE TABLE cha ("
            "channel_id VARCHAR(255), "
            "channel_name VARCHAR(255), "
            "Playlist_id VARCHAR(255), "
            "subscription_count INT, "
            "views INT, "
            "Total_videos INT, "
            "channel_description TEXT, "
            "country TEXT);"
        )
        create_table("cha", channel_details_query)

        # Create video_details table
        video_details_query = (
            "CREATE TABLE vide ("
            "channel_name VARCHAR(255), "
            "channel_id VARCHAR(255), "
            "video_id VARCHAR(255), "
            "title VARCHAR(255), "
            "thumbnail VARCHAR(255), "
            "video_description TEXT, "
            "published_date VARCHAR(255), "
            "Duration VARCHAR(255), "
            "views INT, "
            "likes INT, "
            "comments INT, "
            "favorite_count INT, "
            "Definition VARCHAR(255), "
            "Caption_status VARCHAR(255));"
        )
        create_table("vide", video_details_query)

        # Create comments_details table
        comments_details_query = (
            "CREATE TABLE comme ("
            "comment_Id VARCHAR(255), "
            "video_Id VARCHAR(255), "
            "comment_text TEXT, "
            "comment_author VARCHAR(255), "
            "comment_posted_date VARCHAR(255), "
            "like_count INT, "
            "Reply_count INT);"
        )
        create_table("comme", comments_details_query)


        def insert_into_cha():
            collections = db.channel_details
            query = """INSERT INTO cha VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"""

            for i in collections.find({"Channel_name": user_inp}, {'_id': 0}):
                mycursor.execute(query, tuple(i.values()))
                mydb.commit()


        def insert_into_vide():
            collections1 = db.video_details
            query1 = """INSERT INTO vide VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

            for i in collections1.find({"Channel_name": user_inp}, {'_id': 0}):
                mycursor.execute(query1, tuple(i.values()))
                mydb.commit()


        def insert_into_comme():
            collections1 = db.video_details
            collections2 = db.comments_details
            query2 = """INSERT INTO comme VALUES(%s,%s,%s,%s,%s,%s,%s)"""

            for vid in collections1.find({"Channel_name": user_inp}, {'_id': 0}):
                for i in collections2.find({'Video_id': vid['Video_id']}, {'_id': 0}):
                    mycursor.execute(query2, tuple(i.values()))
                    mydb.commit()


        if st.button("Submit"):
            try:
                insert_into_cha()
                insert_into_vide()
                insert_into_comme()

                st.success("Transformation to MySQL Successful !!")
                

            except:
                st.error("Channel details already transformed !!")

# VIEW PAGE
if selected == "SQL Query":

    st.write("## :black[💡 Pick a Question to Explore]")
    questions = st.selectbox('Query ❓',
                             ['1. What are the names of all the videos and their corresponding channels?',
                              '2. Which channels have the most number of videos, and how many videos do they have?',
                              '3. What are the top 10 most viewed videos and their respective channels?',
                              '4. How many comments were made on each video, and what are their corresponding video names?',
                              '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
                              '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
                              '7. What is the total number of views for each channel, and what are their corresponding channel names?',
                              '8. What are the names of all the channels that have published videos in the year 2022?',
                              '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                              '10. Which videos have the highest number of comments, and what are their corresponding channel names?'])

    if questions == '1. What are the names of all the videos and their corresponding channels?':
        mycursor.execute("""SELECT title AS Video_Title, channel_name AS Channel_Name
                            FROM vide
                            ORDER BY channel_name""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '2. Which channels have the most number of videos, and how many videos do they have?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, total_videos AS Total_Videos
                            FROM cha
                            ORDER BY total_videos DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)


    elif questions == '3. What are the top 10 most viewed videos and their respective channels?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, title AS Video_Title, views AS Views 
                            FROM vide
                            ORDER BY views DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)


    elif questions == '4. How many comments were made on each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT a.video_id AS Video_id, a.title AS Video_Title, b.Total_Comments
                            FROM vide AS a
                            LEFT JOIN (SELECT video_id,COUNT(comment_id) AS Total_Comments
                            FROM comme GROUP BY video_id) AS b
                            ON a.video_id = b.video_id
                            ORDER BY b.Total_Comments DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name,title AS Title,likes AS Likes_Count 
                            FROM vide
                            ORDER BY likes DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)


    elif questions == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT title AS Title, likes AS Likes_Count
                            FROM vide
                            ORDER BY likes DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, views AS Views
                            FROM cha
                            ORDER BY views DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)


    elif questions == '8. What are the names of all the channels that have published videos in the year 2022?':
        mycursor.execute("""SELECT channel_name,published_date
                            FROM vide
                            WHERE YEAR(published_date) = 2022""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name,
                            AVG(duration)/60 AS "Average_Video_Duration (mins)"
                            FROM vide
                            GROUP BY channel_name
                            ORDER BY AVG(duration)/60 DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)



    elif questions == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name,video_id AS Video_ID,comments AS Comments
                            FROM vide
                            ORDER BY comments DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)