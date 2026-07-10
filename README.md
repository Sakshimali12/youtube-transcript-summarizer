# 🎥 YouTube Video Sentiment and AI Summarization

## 📑 Table of Contents

- Overview
- Features
- Technologies Used
- Installation
- Usage
- Project Workflow
- Future Enhancements

---

## 📝 Overview

The **YouTube Video Sentiment and AI Summarization** project is a Python-based web application developed using **Streamlit**. It allows users to analyze any public YouTube video by extracting its transcript, generating an AI-powered summary using **Google Gemini**, performing sentiment analysis on YouTube comments, and displaying important video statistics through an interactive dashboard.

The application provides users with a quick understanding of a video's content and audience feedback without watching the entire video.

---

## ✨ Features

- 🎥 Analyze any public YouTube video using its URL.
- 📝 Extract video transcripts automatically.
- 🤖 Generate AI-powered summaries using Google Gemini.
- 💬 Perform sentiment analysis on YouTube comments.
- 📊 Display positive, negative, and neutral comment distribution.
- 📈 Show video statistics such as title, views, likes, upload date, and duration.
- 🖼 Display the video thumbnail.
- 📋 View top positive and negative comments.
- ⚠ Handle invalid URLs, missing transcripts, and API errors gracefully.
- 🎨 Interactive and user-friendly Streamlit interface.

---

## 🛠 Technologies Used

- Python
- Streamlit
- Google Gemini API
- YouTube Data API v3
- YouTube Transcript API
- NLTK
- Matplotlib
- Pandas
- python-dotenv

---

## ⚙ Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/youtube-video-sentiment-and-summarization.git
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Create a `.env` file

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
```

4. Run the application

```bash
streamlit run app.py
```

---

## 🚀 Usage

1. Launch the application.
2. Paste a YouTube video URL.
3. Click **Analyze Video**.
4. View video details and sentiment analysis.
5. Click **Generate Detailed Summary** to get the AI-generated summary.

---

## 🔄 Project Workflow

```
YouTube URL
      │
      ▼
Extract Video ID
      │
      ▼
Fetch Video Details
      │
      ▼
Extract Transcript
      │
      ▼
Generate Summary using Google Gemini
      │
      ▼
Fetch Comments
      │
      ▼
Perform Sentiment Analysis
      │
      ▼
Display Results on Streamlit Dashboard
```

---

## 🚀 Future Enhancements

- Download summary as PDF.
- Support multiple languages.
- Keyword extraction.
- Speech-to-text improvements.
- Dashboard analytics.
- Real-time sentiment visualization.

---

## 👩‍💻 Developed By

**Sakshi Mali**
