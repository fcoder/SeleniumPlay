# get_yt_duration.py
# Folder ..<local_chinesesong_dir/tools/selenium is for this small program.
# Do source venv/bin/active to get the venv for this program
# This program first visits Chinesesong.net to get the html for each song, from
# which it find out the video_id for each embedded YouTube video, then use the
# video to make URLs for the song or bonus at Youtube.
#
# It is possible to get duration of embedded Youtube video inside the pages from
# www.chinesesong.net, but the code is harder to implement and understand

import time
from   pytube import YouTube       # pip install pytube
from   bs4 import BeautifulSoup    # pip install beautifulsoup4
import requests                    # pip install requests
import webbrowser
import urllib.parse

youtube_api_key="AIzaSyBsU4svkh34KS9EiMKWy4UKDyBKQbF2WVU"

base_url = "https://www.chinesesong.net"

# Called by get_video_details below
def parse_duration(duration):
    import isodate                 # pip install isodate
    return isodate.parse_duration(duration).total_seconds()

# Called by get_video_duration below
def extract_video_id(url):
    parsed_url = urllib.parse.urlparse(url)
    video_id = parsed_url.path.split("/")[-1]  # Extract the last part of the path
    if "?" in video_id:                        # Remove query parameters, if any
        video_id = video_id.split("?")[0]
    return video_id

# Called by get_video_duration below  
def get_video_details(video_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=snippet,contentDetails&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            content_details = data["items"][0]["contentDetails"]
            snippet = data["items"][0]["snippet"]
            duration = parse_duration(content_details["duration"])  # parse_duration is defined above
            title = snippet["title"]
            return title, duration
        else:
            print(f"Video ID {video_id} is unavailable or private.")
    else:
        print(f"Failed to fetch video details. Status code: {response.status_code}")
    return None, None

#! Called by selenium_play.py
# First get a song from our own web server, then figure out the Youtube URL, convert it from embedded
# YouTube URL to regular YouTube URL, then open a Browser tab to play for the length of the video
def get_video_duration(song_url):
  # Fetch the song page
  response = requests.get(song_url)
  soup     = BeautifulSoup(response.content, 'html.parser')
  iframe   = soup.find('iframe')              # Extract the embedded YouTube iframe src
  
  if iframe:
    video_url = iframe['src']
    # print(f"get_yt_video_duration: Found video: {video_url}")

    # Use pytube to fetch the video metadata. get_video_details is defined above
    video_id = extract_video_id(video_url)
    youtube = YouTube(f"https://www.youtube.com/watch?v={video_id}")

    # Fetch video duration, get_video_details is defined above
    title, duration = get_video_details(video_id, youtube_api_key) 

    # Wait for the video duration before proceeding to the next one
    ##### time.sleep(duration)
    return duration
  else:
    print("Error: did not find iframe")
    return None