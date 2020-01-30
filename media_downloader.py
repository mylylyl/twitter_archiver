import youtube_dl
from pathlib import Path
from requests import get

PHOTO_BASE_URL = "https://pbs.twimg.com/media/"
VIDEO_BASE_URL = "https://twitter.com/statuses/"

def video(video_url : str, download_location : str):
    download_path = str(Path(download_location, "%(id)s.%(ext)s"))
    ydl_opts = {
        "outtmpl": download_path,
        "quiet": True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url, ])

def photo(photo_name : str, download_location : str):
    path = str(Path(download_location, photo_name + ".jpg"))
    if not Path(path).is_file():
        with open(path, "wb") as file:
            file.write(get(PHOTO_BASE_URL + photo_name + ".jpg").content)