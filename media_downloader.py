from urllib import request
import pathlib
import requests
import sys
import os
import re
import json
from http.client import IncompleteRead

PHOTO_RE = r'https:\/\/pbs\.twimg\.com\/media\/([a-zA-Z0-9-_]*)\.(jpg|png)'

def video(id: str, video_info: json,  download_location : str) -> bool:
    if not pathlib.Path(download_location).exists():
        os.mkdir(download_location)
    download_path = str(pathlib.Path(download_location, '%s.mp4' % id))
    if pathlib.Path(download_path).exists():
        return False

    if 'variants' not in video_info:
        print('[x] failed to download video (%s) because video_info is invalid' % (id))
        return False

    # find the best variants
    url = ''
    bitrate = 0
    for var in video_info['variants']:
        if 'bitrate' in var:
            if var['bitrate'] > bitrate:
                url = var['url']
                bitrate = var['bitrate']

    try:
        request.urlretrieve(url, download_path)
    except:
        print("[x] failed to download video (%s) to (%s) because an exception happened: %s" % (id, download_location, sys.exc_info()[0]))
        return False
    
    #print('[√] finished downloading video %s' % url)
    return True

def _photo(url: str, path: str) -> bool:
    try:
        with open(path, 'wb') as file:
            file.write(requests.get(url).content)
    except:
        print('[x] failed to download photo (%s) because an unexpected exception happened: %s' % (url, sys.exc_info()[0]))
        return False
    
    return True

def tweet_photo(url: str, download_location: str) -> bool:
    if not pathlib.Path(download_location).exists():
        os.mkdir(download_location)
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
