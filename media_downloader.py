import youtube_dl
from pathlib import Path
from requests import get
from urllib.parse import urlparse

def video(video_url : str, download_location : str):
    download_path = str(Path(download_location, "%(id)s.%(ext)s"))
    ydl_opts = {
        "outtmpl": download_path,
        "quiet": True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url, ])

def photo(photo_url : str, download_location : str):
    url_obj = urlparse(photo_url)
    file_name = url_obj.path.replace("/media/", "")
    path = str(Path(download_location, file_name))
    if not Path(path).is_file():
        with open(path, "wb") as file:
            file.write(get(photo_url).content)