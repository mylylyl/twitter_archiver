import youtube_dl
import pathlib
import requests
from http.client import IncompleteRead

PHOTO_BASE_URL = "https://pbs.twimg.com/media/"
VIDEO_BASE_URL = "https://twitter.com/statuses/"

def video(video_id : int, download_location : str) -> bool:
    download_path = str(pathlib.Path(download_location, "%(id)s.%(ext)s"))
    ydl_opts = {
        "outtmpl": download_path,
        "quiet": True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([VIDEO_BASE_URL + str(video_id), ])
        except youtube_dl.utils.DownloadError as e:
            print("[x] failed to download", video_id, " because an exception happened: ", e)
            return False
        except:
            print("[x] failed to download", video_id, " because an unexpected exception happened: ", sys.exc_info())
            return False
        else:
            return True

def photo(photo_name : str, download_location : str) -> bool:
    path = str(pathlib.Path(download_location, photo_name + ".jpg"))
    if not pathlib.Path(path).is_file():
        with open(path, "wb") as file:
            try:
                file.write(requests.get(PHOTO_BASE_URL + photo_name + ".jpg").content)
            except:
                print("[x] failed to download", photo_name, " because an unexpected exception happened: ", sys.exc_info())
                return False
            else:
                return True