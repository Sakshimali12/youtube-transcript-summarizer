# ==========================
# IMPORT LIBRARIES
# ==========================

import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
from googleapiclient.discovery import build
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import isodate
import time
from googleapiclient.errors import HttpError
from dateutil import parser
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="🎥 YouTube Video Sentiment and Summarization",
    layout="centered"
)
# ==========================
# DOWNLOAD NLTK DATA
# ==========================

try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")
# ==========================
# LOAD ENVIRONMENT VARIABLES
# ==========================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY not found")
    st.stop()

if not YOUTUBE_API_KEY:
    st.error("YOUTUBE_API_KEY not found")
    st.stop()

# ==========================
# CONFIGURE GEMINI
# ==========================

genai.configure(api_key=GOOGLE_API_KEY)

# ==========================
# YOUTUBE API
# ==========================

youtube = build(
    "youtube",
    "v3",
    developerKey=YOUTUBE_API_KEY
)

# ==========================
# GEMINI PROMPT
# ==========================

prompt = """
You are a professional YouTube Video Summarizer.

Read the transcript carefully and generate a clean summary.

Requirements:

• Explain the complete video in simple English.

• Use bullet points.

• Mention important concepts.

• Keep summary around 300 words.

Transcript:
"""

# ==========================
# GEMINI FUNCTION
# ==========================

def get_gemini_response(transcript_text, prompt):

    try:

        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content(
            prompt + "\n\n" + transcript_text
        )

        return response.text

    except Exception as e:

        return f"Gemini Error : {e}"

# ==========================
# TRANSCRIPT FUNCTION
# (Latest youtube-transcript-api)
# ==========================

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled
)

def extract_transcript_details(video_id):

    try:

        api = YouTubeTranscriptApi()

        # Get all available transcripts
        transcript_list = api.list(video_id)

        # Try Hindi first
        try:
            transcript = transcript_list.find_transcript(["hi"])

        except NoTranscriptFound:

            # If Hindi not available, try English
            transcript = transcript_list.find_transcript(
                ["en", "en-US", "en-GB"]
            )

        fetched = transcript.fetch()

        transcript = ""

        for item in fetched:

            if hasattr(item, "text"):
                transcript += item.text + " "
            else:
                transcript += item["text"] + " "

        return transcript.strip()

    except TranscriptsDisabled:

        raise Exception("Transcript is disabled for this video.")

    except NoTranscriptFound:

        raise Exception(
            "No transcript available in Hindi or English."
        )

    except Exception as e:

        raise Exception(f"Transcript Error : {e}")
    # ==========================================
# EXTRACT VIDEO ID
# ==========================================

def extract_video_id(youtube_url):

    patterns = [
        r"v=([^&]+)",
        r"youtu\.be/([^?]+)"
    ]

    for pattern in patterns:

        match = re.search(pattern, youtube_url)

        if match:
            return match.group(1)

    return None


# ==========================================
# GET VIDEO DETAILS
# ==========================================

def get_video_details(video_id, retries=3):

    for attempt in range(retries):

        try:

            request = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )

            response = request.execute()

            if len(response["items"]) == 0:
                raise Exception("Video not found.")

            video_data = response["items"][0]

            duration = isodate.parse_duration(
                video_data["contentDetails"]["duration"]
            )

            formatted_duration = (
                f"{int(duration.total_seconds()//60)}:"
                f"{int(duration.total_seconds()%60):02}"
            )

            upload_date = parser.parse(
                video_data["snippet"]["publishedAt"]
            ).strftime("%Y-%m-%d")

            return {

                "title": video_data["snippet"]["title"],

                "channel_title": video_data["snippet"]["channelTitle"],

                "view_count": video_data["statistics"].get("viewCount", "0"),

                "upload_date": upload_date,

                "duration": formatted_duration,

                "like_count": video_data["statistics"].get("likeCount", "N/A"),

                "dislike_count": video_data["statistics"].get("dislikeCount", "N/A")

            }

        except HttpError as e:

            if e.resp.status in [500, 503]:
                time.sleep(2 ** attempt)

            else:
                raise

    raise Exception("Unable to fetch video details.")


# ==========================================
# GET VIDEO COMMENTS
# ==========================================

def get_video_comments(video_id):

    comments = []

    try:

        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100
        )

        while request:

            response = request.execute()

            for item in response["items"]:

                comment = item["snippet"]["topLevelComment"]["snippet"]["textOriginal"]

                comments.append(comment)

            request = youtube.commentThreads().list_next(
                request,
                response
            )

    except Exception:
        pass

    return comments









# ==========================================
# SENTIMENT ANALYSIS
# ==========================================

def analyze_sentiment(comments):

    sid=SentimentIntensityAnalyzer()

    positive=[]

    negative=[]

    neutral=[]

    for comment in comments:

        score=sid.polarity_scores(comment)["compound"]

        if score>=0.05:

            positive.append(comment)

        elif score<=-0.05:

            negative.append(comment)

        else:

            neutral.append(comment)

    return (

        len(positive),

        len(negative),

        len(neutral),

        positive,

        negative

    )


# ==========================================
# TOP COMMENTS
# ==========================================

def get_top_comments(positive,negative):

    return positive[:3],negative[:3]


# ==========================================
# PIE CHART
# ==========================================

def plot_sentiment_pie_chart(

    positive,

    negative,

    neutral

):

    labels=[

        "😊 Positive",

        "😠 Negative",

        "😐 Neutral"

    ]

    sizes=[

        positive,

        negative,

        neutral

    ]

    colors=[

        "#DFF0D8",

        "#F2DEDE",

        "#EAEAEA"

    ]

    explode=(0.08,0,0)

    fig,ax=plt.subplots(figsize=(5,5))

    ax.pie(

        sizes,

        labels=labels,

        colors=colors,

        autopct="%1.1f%%",

        explode=explode,

        startangle=140

    )

    ax.axis("equal")

    return fig
# ==========================================
# STREAMLIT PAGE
# ==========================================



st.markdown(
    """
    <h1 style='text-align:center;color:#FF5733;'>
    🎥 YouTube Video Sentiment and Summarization 🎯
    </h1>
    """,
    unsafe_allow_html=True
)

# ==========================================
# SESSION STATE
# ==========================================

if "responses" not in st.session_state:
    st.session_state.responses = []

# ==========================================
# INPUT BOX
# ==========================================

youtube_link = st.text_input(
    "🔗 Enter YouTube Video URL"
)

# ==========================================
# ANALYZE BUTTON
# ==========================================

if st.button("🔍 Analyze Video"):

    if youtube_link.strip() == "":

        st.warning("Please enter a YouTube Link.")

    else:

        video_id = extract_video_id(youtube_link)

        if not video_id:

            st.error("Invalid YouTube URL")

        else:

            with st.spinner("Collecting Video Information..."):

                try:

                    thumbnail_url = (
                        f"https://img.youtube.com/vi/{video_id}/0.jpg"
                    )

                    video_details = get_video_details(video_id)

                    comments = get_video_comments(video_id)

                    (
                        positive_count,
                        negative_count,
                        neutral_count,
                        positive_comments,
                        negative_comments

                    ) = analyze_sentiment(comments)

                    (
                        top_positive,
                        top_negative

                    ) = get_top_comments(

                        positive_comments,

                        negative_comments

                    )

                    response = {

                        "video_id": video_id,

                        "thumbnail_url": thumbnail_url,

                        "video_details": video_details,

                        "comments": {

                            "total_comments": len(comments),

                            "positive_comments": positive_count,

                            "negative_comments": negative_count,

                            "neutral_comments": neutral_count,

                            "positive_comments_list": top_positive,

                            "negative_comments_list": top_negative

                        }

                    }

                    st.session_state.responses = [response]

                    st.success("Video Analyzed Successfully ✅")

                except Exception as e:

                    st.error(str(e))
                    # ==========================================
# DISPLAY VIDEO INFORMATION
# ==========================================

for idx, response in enumerate(st.session_state.responses):

    video_details = response["video_details"]
    comments = response["comments"]

    st.image(response["thumbnail_url"])

    st.markdown("## 📹 Video Title")
    st.write(video_details["title"])

    st.markdown("## 📺 Channel Name")
    st.write(video_details["channel_title"])

    st.markdown("## 👁 Views")
    st.write(video_details["view_count"])

    st.markdown("## 📅 Upload Date")
    st.write(video_details["upload_date"])

    st.markdown("## ⏱ Duration")
    st.write(video_details["duration"])

    st.markdown("## 👍 Likes")
    st.write(video_details["like_count"])

    st.markdown("## 👎 Dislikes")
    st.write(video_details["dislike_count"])

    st.markdown("## 💬 Total Comments")
    st.write(comments["total_comments"])

    # ==========================================
    # PIE CHART
    # ==========================================

    fig = plot_sentiment_pie_chart(

        comments["positive_comments"],

        comments["negative_comments"],

        comments["neutral_comments"]

    )

    st.pyplot(fig)

    st.markdown("### 😊 Positive Comments")
    st.success(
        f'{comments["positive_comments"]} Comments'
    )

    st.markdown("### 😠 Negative Comments")
    st.error(
        f'{comments["negative_comments"]} Comments'
    )

    st.markdown("### 😐 Neutral Comments")
    st.info(
        f'{comments["neutral_comments"]} Comments'
    )

    # ==========================================
    # SHOW TOP COMMENTS
    # ==========================================

    show_comments = st.checkbox(

        "Show Top Comments",

        key=f"comments_{idx}"

    )

    if show_comments:

        st.subheader("👍 Top Positive Comments")

        if len(comments["positive_comments_list"]) == 0:

            st.write("No Positive Comments Found")

        else:

            for comment in comments["positive_comments_list"]:

                st.success(comment)

        st.subheader("👎 Top Negative Comments")

        if len(comments["negative_comments_list"]) == 0:

            st.write("No Negative Comments Found")

        else:

            for comment in comments["negative_comments_list"]:

                st.error(comment)

    # ==========================================
    # GENERATE SUMMARY BUTTON
    # ==========================================


    # ==========================================
    # DISPLAY SUMMARY
    # ==========================================

   
        # -----------------------------
# Generate Summary
# -----------------------------
    if 'gemini_response' not in response:
        if st.button("📑 Generate Detailed Summary", key=f"btn_{idx}"):

            with st.spinner("Generating Summary..."):

                video_id = extract_video_id(youtube_link)

                if video_id:
                    try:
                        transcript = extract_transcript_details(video_id)

                        gemini_response = get_gemini_response(
                            transcript,
                            prompt
                        )

                        response["gemini_response"] = gemini_response
                        st.session_state.responses[idx] = response

                    except Exception as e:
                        import traceback

                        st.error(str(e))
                        st.code(traceback.format_exc())

                else:
                    st.error("Invalid YouTube URL")

    # -----------------------------
    # Show Summary
    # -----------------------------
    if "gemini_response" in response:

        st.markdown(
            "<h2 style='color:#1E90FF;'>📜 Summary</h2>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div style="
                background:#F0F8FF;
                padding:15px;
                border-radius:10px;
                color:black;
            ">
            {response['gemini_response']}
            </div>
            """,
            unsafe_allow_html=True
        )