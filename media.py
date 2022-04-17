from threading import Thread
from queue import Queue

from base import Base
import media_downloader as downloader
from api import TwitterAPI

THREADS = 10
class MediaType:
    def __init__(self, type: str, info1: str, info2):
        self.type = type
        self.info1 = info1
        self.info2 = info2

class MediaWorker(Thread):
    def __init__(self, queue: Queue, media_dir: str):
        Thread.__init__(self)
        self.queue = queue
        self.media_dir = media_dir

    def run(self):
        while True:
            mt = self.queue.get()
            if mt.type == "video":
                downloader.video(mt.info1, mt.info2, self.media_dir)
            elif mt.type == "photo":
                downloader.tweet_photo(mt.info1, self.media_dir)
            self.queue.task_done()

class MediaScheduler(object):
    def __init__(self, entries_count: int, media_dir: str):
        self.queue = Queue()

        for _ in range(min(THREADS, entries_count)):
            worker = MediaWorker(self.queue, media_dir)
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

        ms = MediaScheduler(len(self.tweets_json), self.media_dir)

        for entry in self.tweets_json:
            tweet_obj = entry['content']['itemContent']['tweet_results']['result']
            tweet_id = tweet_obj['rest_id']
            tweet = tweet_obj['legacy']
            # the tweets contains retweets which we'll save, but not parse for media downloads
            # the retweets has `user_id_str` different than our `rest_id`
            if tweet['user_id_str'] != self.user_json['rest_id']:
                continue

            if 'extended_entities' not in tweet:
                # there are tweets with no media
                # print('[!] no extended_entities found in tweet %s' % tweet_id)
                continue

            medias = tweet['extended_entities']['media']
            if len(medias) == 0:
                # no media
                continue
            
            # https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/overview/extended-entities-object#intro
            # media has 3 types: ‘photo’, ‘video’ or ‘animated_gif’
            for media in medias:
                if media['type'] == 'video':
                    # downloader.video(tweet_id, media['video_info'], self.media_dir)
                    ms.queue.put(MediaType(media['type'], tweet_id, media['video_info']))
                elif media['type'] == 'photo':
                    # downloader.tweet_photo(media['media_url_https'], self.media_dir)
                    ms.queue.put(MediaType(media['type'], media['media_url_https'], None))

        ms.queue.join()