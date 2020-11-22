import youtube_dl
import pathlib
import requests
import sys
import re
from http.client import IncompleteRead

PHOTO_RE = r'https:\/\/pbs\.twimg\.com\/media\/([a-zA-Z0-9-_]*)\.(jpg|png)'

def video(url : str, id: str, download_location : str) -> bool:
    download_path = str(pathlib.Path(download_location, '%s.mp4' % id))
    if pathlib.Path(download_path).is_file():
        return False

    ydl_opts = {
        'format': 'bestaudio/best',
        "outtmpl": download_path,
        "quiet": True,
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url, ])
    except youtube_dl.utils.DownloadError as e:
        #print("[x] failed to download video (%s) because an exception happened: %s" % (url, e))
        return False
    except:
        #print("[x] failed to download video (%s) because an exception happened: %s" % (url, sys.exc_info()[0]))
        return False
    
    #print('[√] finished downloading video %s' % url)
    return True

def _photo(url : str, path : str) -> bool:
    try:
        with open(path, 'wb') as file:
            file.write(requests.get(url).content)
    except:
        print('[x] failed to download photo (%s) because an unexpected exception happened: %s' % (url, sys.exc_info()[0]))
        return False
    
    return True

def tweet_photo(url : str, download_location : str) -> bool:
    x = re.search(PHOTO_RE, url)
    if x is None:
        print('[!] unknown url recorded %s' % url)
        return False

    path = str(pathlib.Path(download_location, '%s.jpg' % x.group(1)))
    if pathlib.Path(path).is_file():
        return False

    return _photo(url, path)

def avatar_photo(url : str, download_location : str) -> bool:
    path = str(pathlib.Path(download_location, 'avatar.jpg'))
    return _photo(url, path)

def banner_photo(url : str, download_location : str) -> bool:
    path = str(pathlib.Path(download_location, 'banner.jpg'))
    return _photo(url, path)
            