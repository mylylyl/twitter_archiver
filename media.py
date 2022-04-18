import pathlib
from threading import Thread
from queue import Queue

from base import Base
import media_downloader as downloader
from api import TwitterAPI
import utils

THREADS = 10
class MediaType:
    def __init__(self, type: str, info1: str, info2, media_dir: str):
        self.type = type
        self.info1 = info1
        self.info2 = info2
        self.media_dir = media_dir

class MediaWorker(Thread):
    def __init__(self, queue: Queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            mt = self.queue.get()
            if mt.type == "video":
                downloader.video(mt.info1, mt.info2, mt.media_dir)
            elif mt.type == "photo":
                downloader.tweet_photo(mt.info1, mt.media_dir)
            self.queue.task_done()

class MediaScheduler(object):
    def __init__(self, entries_count: int):
        self.queue = Queue()

        for _ in range(min(THREADS, entries_count)):
            worker = MediaWorker(self.queue)
            worker.daemon = True
            worker.start()

class Media(Base):
    def __init__(self, username : str, api : TwitterAPI):
        Base.__init__(self, username, api)

    def archive(self) -> bool:
        if self._read_user_json() is False:
            print('[!] failed to read user json for %s' % self.username)
            return False

        if self._read_tweets_json() is False:
            print('[!] failed to read tweets json for %s' % self.username)
            return False

        ms = MediaScheduler(len(self.tweets_json))

        for entry in self.tweets_json:
            tweet_obj = entry['content']['itemContent']['tweet_results']['result']
            tweet_id = tweet_obj['rest_id']
            tweet = tweet_obj['legacy']

            if 'extended_entities' not in tweet:
                # there are tweets with no media
                # print('[!] no extended_entities found in tweet %s' % tweet_id)
                continue

            medias = tweet['extended_entities']['media']
            if len(medias) == 0:
                # no media
                continue

            media_dir = self.media_dir

            # the tweets is a retweet
            if 'retweeted_status_result' in tweet:
                retweet = tweet['retweeted_status_result']
                if utils.has_keys(retweet, ['result', 'core', 'user_results', 'result', 'legacy']):
                    rt_username = retweet['result']['core']['user_results']['result']['legacy']['screen_name']
                    media_dir = str(pathlib.Path(self.parent_dir, rt_username))
                else:
                    print('[!] invalid retweet for %s: %s' % (self.username, retweet))
            
            # https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/overview/extended-entities-object#intro
            # media has 3 types: ‘photo’, ‘video’ or ‘animated_gif’
            for media in medias:
                if media['type'] == 'video':
                    ms.queue.put(MediaType(media['type'], tweet_id, media['video_info'], media_dir))
                elif media['type'] == 'photo':
                    ms.queue.put(MediaType(media['type'], media['media_url_https'], None, media_dir))

        ms.queue.join()