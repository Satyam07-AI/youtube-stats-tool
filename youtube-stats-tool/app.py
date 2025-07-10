from flask import Flask, render_template, request
from googleapiclient.discovery import build
import re, requests, json

app = Flask(__name__)

API_KEY = "YOUR_API_KEY"

def extract_video_id(url):
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def fetch_video_data(video_id):
    youtube = build("youtube", "v3", developerKey=API_KEY)
    request = youtube.videos().list(part="snippet,statistics,contentDetails", id=video_id)
    response = request.execute()
    if not response["items"]:
        return None
    video = response["items"][0]
    data = {
        "title": video["snippet"]["title"],
        "channel": video["snippet"]["channelTitle"],
        "views": video["statistics"]["viewCount"],
        "likes": video["statistics"].get("likeCount", "Hidden"),
        "upload_date": video["snippet"]["publishedAt"],
        "description": video["snippet"]["description"][:300],
        "duration": video["contentDetails"]["duration"],
        "tags": video["snippet"].get("tags", []),
        "thumbnail": video["snippet"]["thumbnails"]["high"]["url"]
    }
    return data

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    error = None
    if request.method == "POST":
        url = request.form["url"]
        video_id = extract_video_id(url)
        if not video_id:
            error = "Invalid YouTube URL"
        else:
            data = fetch_video_data(video_id)
            if not data:
                error = "Video not found or restricted."
    return render_template("index.html", data=data, error=error)

if __name__ == "__main__":
    app.run(debug=True)
# Temporary fix for Render deployment
