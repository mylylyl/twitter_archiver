import json
import sys
import requests

from base import Base
import api

class Tweets(Base):
    def __init__(self, username : str):
        Base.__init__(self, username)

    def archive(self) -> bool:
        if self._read_user_json() is False:
            #print('[!] failed to read user json for %s, skipping archive' % self.username)
            return False

        has_tweets = self._read_tweets_json()
        #if has_tweets is False:
        #    print('[.] %s was not archived before' % self.username)
        #else:
        #    print('[.] %s has %d tweets archived' % (self.username, len(self.tweets_json)))

        print('[.] getting tweets for %s (display_name: %s, follower: %d, following: %d)' 
                % (self.username, self.user_json['legacy']['name'], self.user_json['legacy']['followers_count'], self.user_json['legacy']['friends_count']))

        resp = api.get_tweets(self.user_json['rest_id'], 9999)

        if resp.status_code != 200:
            print('[!] unable to get user object for %s: status code %d' % (self.username, resp.status_code))
            return False
        
        if len(resp.text) <= 0:
            print('[!] invalid response for %s: %s' % (self.username, resp.text))
            return False

        data = json.loads(resp.text)
        if 'globalObjects' not in data or 'tweets' not in data['globalObjects']:
            print('[!] invalid json response for %s: %s' % (self.username, resp.text))
            return False

        tweets = data['globalObjects']['tweets']
        #print('[.] getting %d tweets for %s. we have archived %d tweets' % (len(tweets), self.username, len(self.tweets_json) if has_tweets else 0))
        
        if has_tweets is True:
            # merge the two json
            tweets = {**tweets, **self.tweets_json}
        #print('[.] there are %d newly acquired tweets' % (len(tweets) - len(self.tweets_json) if has_tweets else 0))

        with open(self.tweets_json_filename, 'w') as outfile:
            json.dump(tweets, outfile)
            #print('[√] refreshed tweets json for %s' % self.username)
            return True

        print('[!] failed to open file `%s` for %s' % (self.tweets_json_filename, self.username))
        return False

        
