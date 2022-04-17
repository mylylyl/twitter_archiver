import os
import json
from api import TwitterAPI
from base import Base
import media_downloader as downloader

# parse v2 json and check for missing media files
data_dir = 'data.v2'

def download_media(username : str, api : TwitterAPI):
    b = Base(username, api)
    b._change_parent_dir(data_dir)

    if b._read_user_json() is False:
        print('[!] failed to read user json for %s' % b.username)
        return False

    if b._read_tweets_json() is False:
        print('[!] failed to read tweets json for %s' % b.username)
        return False

    for tweet_id in b.tweets_json:
        tweet = b.tweets_json[tweet_id]
        # the tweets contains retweets which we'll save, but not parse for media downloads
        # the retweets has `user_id_str` different than our `rest_id`
        if tweet['user_id_str'] != b.user_json['rest_id']:
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
                downloader.video(tweet_id, media['video_info'], b.media_dir)
            elif media['type'] == 'photo':
                downloader.tweet_photo(media['media_url_https'], b.media_dir)

config = {}
with open('config.json', 'r') as f:
    config_file = f.read()
    config = json.loads(config_file)

api = TwitterAPI(config["graphql_userbyscreenname_endpoint"], config["graphql_usertweets_endpoint"], config["graphql_tweetdetail_endpoint"], config["bearer_token"])
if not api.get_guest_token():
    print('[!] failed to retrive guest token')
else:
    dirs = os.listdir(data_dir)
    for dir in dirs:
        download_media(dir, api)
