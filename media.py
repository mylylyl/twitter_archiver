import pathlib
import os

from base import Base
from api import TwitterAPI
from media_scheduler import MediaInfo, MediaScheduler, MediaType
import utils

# number of media worker thread
MEDIA_THREADS = 4

class Media(Base):
    def __init__(self, username: str, api: TwitterAPI):
        Base.__init__(self, username, api)

    def archive(self) -> bool:
        if self._read_user_json() is False:
            print('[!] failed to read user json for %s' % self.username)
            return False

        if self._read_tweets_json() is False:
            print('[!] failed to read tweets json for %s' % self.username)
            return False

        ms = MediaScheduler()
        ms.start_workers(MEDIA_THREADS)

        # we make sure there's no duplicates
        # image/video url is used here as unique identifier
        duplicates = set()

        for entry in self.tweets_json:
            if type(entry) == type(''):
                print('[x] %s is not v3' % self.username)
                return False

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

            isRetweet = False
            media_dir = self.media_dir

            # the tweets is a retweet
            if 'retweeted_status_result' in tweet:
                retweet = tweet['retweeted_status_result']
                if utils.has_keys(retweet, ['result', 'core', 'user_results', 'result', 'legacy']):
                    rt_username = retweet['result']['core']['user_results']['result']['legacy']['screen_name']
                    media_dir = str(pathlib.Path(self.parent_dir, rt_username))
                    isRetweet = True
                else:
                    print('[!] invalid retweet for %s: %s' % (self.username, retweet))
                    continue

            if not pathlib.Path(media_dir).exists():
                os.mkdir(media_dir)
            
            # https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/overview/extended-entities-object#intro
            # media has 3 types: ‘photo’, ‘video’ or ‘animated_gif’
            for media in medias:
                if media['type'] == 'video':
                    if 'variants' not in media['video_info']:
                        print('[x] failed to download video (%s) for %s because video_info is invalid' % (tweet_id, self.username))
                        continue

                    # find the best variants
                    url = ''
                    bitrate = 0
                    for var in media['video_info']['variants']:
                        if 'bitrate' in var:
                            if var['bitrate'] > bitrate:
                                url = var['url']
                                bitrate = var['bitrate']
                    # get source id instead of the retweet id so we don't create duplicates
                    id_str = media['source_status_id_str'] if isRetweet else tweet['id_str']

                    if url not in duplicates:
                        duplicates.add(url)
                        ms.queue.put(MediaInfo(MediaType.VIDEO, url, media_dir, id_str))
                elif media['type'] == 'photo':
                    url = media['media_url_https']
                    if url not in duplicates:
                        duplicates.add(url)
                        ms.queue.put(MediaInfo(MediaType.PHOTO, url, media_dir, ''))

        ms.queue.join()
        return True