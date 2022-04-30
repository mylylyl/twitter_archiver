from urllib import request
import pathlib
from urllib.error import ContentTooShortError, HTTPError
import requests
import sys
import re
import json
import os

PHOTO_RE = r'https:\/\/pbs\.twimg\.com\/media\/([a-zA-Z0-9-_]*)\.(jpg|png)'
RETRY = 5

def video(url: str, source_video_id: str, download_dir: str) -> bool:
    if not pathlib.Path(download_dir).exists():
        return False

    download_path = pathlib.Path(download_dir, '%s.mp4' % source_video_id)
    if download_path.exists():
        return False

    try:
        request.urlretrieve(url, str(download_path))
    except HTTPError as e:
        # print('[x] failed to download video (%s) to (%s) because a http exception happened: %d %s' % (source_video_id, str(download_path), e.code, e.reason))
        return False
    except ContentTooShortError:
        # @todo add retry
        return False
    except:
        print("[x] failed to download video (%s) to (%s) because an exception happened: %s" % (source_video_id, str(download_path), sys.exc_info()[0]))
        return False
    
    #print('[√] finished downloading video %s' % url)
    return True

def _photo(url: str, path: str, retry: int) -> bool:
    if retry > RETRY:
        return False
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return False
        if len(res.content) == 0:
            print('[x] failed to download photo (%s) because photo size == 0 (retry %d)' % (url, retry))
            return _photo(url, path, retry + 1)
        with open(path, 'wb') as file:
            file.write(res.content)
    except requests.exceptions.ConnectTimeout:
        print('[x] failed to download photo (%s) because time out (retry %d)' % (url, retry))
        return _photo(url, path, retry + 1)
    except HTTPError as e:
        print('[x] failed to download photo (%s) because a http exception happened: %d %s' % (url, e.code, e.reason))
        return False
    except:
        print('[x] failed to download photo (%s) because an unexpected exception happened: %s' % (url, sys.exc_info()[0]))
        return False
    
    return True

def tweet_photo(url: str, download_dir: str) -> bool:
    if not pathlib.Path(download_dir).exists():
        return False

    x = re.search(PHOTO_RE, url)
    if x is None:
        print('[!] unknown url %s found for photo' % url)
        return False

    # we use the image name because there can be multiple images for one tweet
    image_path = x.group(1)

    download_path = pathlib.Path(download_dir, '%s.jpg' % image_path)
    if download_path.exists():
        if download_path.stat().st_size > 1000:
            return False
        os.remove(str(download_path))

    return _photo(url, str(download_path), 0)

def avatar_photo(url: str, download_location: str) -> bool:
    path = str(pathlib.Path(download_location, 'avatar.jpg'))
    return _photo(url, path, 0)

def banner_photo(url: str, download_location: str) -> bool:
    path = str(pathlib.Path(download_location, 'banner.jpg'))
    return _photo(url, path, 0)
