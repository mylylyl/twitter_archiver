from base import Base
import media_downloader as downloader
from api import TwitterAPI

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

        for tweet_id in self.tweets_json:
            tweet = self.tweets_json[tweet_id]
            
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
                    downloader.video(media['expanded_url'], tweet_id, self.media_dir)
                elif media['type'] == 'photo':
                    downloader.tweet_photo(media['media_url_https'], self.media_dir)