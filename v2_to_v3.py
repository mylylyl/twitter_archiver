import os
import json
from api import TwitterAPI
from base import Base
from user import User
from tweets import Tweets

import utils

# parse v2 json and convert to v3
data_dir = 'data'

def create_fake_v3(id: str, legacy):
    template = {
        "entryId": "tweet-%s" % id,
        "sortIndex": id,
        "content": {
            "entryType": "TimelineTimelineItem",
            "itemContent": {
                "itemType": "TimelineTweet",
                "tweet_results": {
                    "result": {
                        "__typename": "Tweet",
                        "rest_id": id,
                        "core": {},
                        "legacy": legacy,
                        "quick_promote_eligibility": {
                            "eligibility": "IneligibleUserUnauthorized"
                        }
                    }
                },
                "tweetDisplayType": "Tweet",
                "ruxContext": ""
            }
        }
    }
    return template

def convert(username : str, api : TwitterAPI):
    t = Tweets(username, api)
    t._change_parent_dir(data_dir)

    if t._read_user_json() is False:
        print('[!] failed to read user json for %s, skip converting' % username)
        return

    archived = t._read_tweets_json()
    if not archived:
        print('[.] %s is not archived, skip converting' % username)
        return

    if type(t.tweets_json) == type([]):
        print('[.] %s already converted, skipping' % username)
        return
    
    statuses_count = t.user_json['legacy']['statuses_count']

    tweets = []
    cursor_value = ""

    while statuses_count != 0:
        resp, remaining = api.get_tweets(t.user_json['rest_id'], statuses_count, cursor_value)

        if resp.status_code != 200:
            print('[!] unable to get user object for %s: status code %d' % (username, resp.status_code))
            break
        
        if len(resp.text) <= 0:
            print('[!] invalid response for %s: %s' % (username, resp.text))
            break

        data = json.loads(resp.text)

        if 'errors' in data:
            print('[!] errors in tweet json response for %s: %s' % (username, data['errors']))
            break

        if not utils.has_keys(data, ['data', 'user', 'result', 'timeline', 'timeline', 'instructions']):
            print('[!] invalid tweet json response for %s: %s' % (username, resp.text))
            break

        instructions: list = data['data']['user']['result']['timeline']['timeline']['instructions']

        # There can be 3 types of instructions
        # TimelineAddEntries for all normal entries(tweets)
        # TimelinePinEntry for the pinned tweet (with only 1 entry)
        # TimelineClearCache for unknown purposes

        if len(instructions) < 0 or len(instructions) > 3:
            print('[!] invalid instructions count for %s: %d' % (self.username, len(instructions)))
            return False

        instruction = utils.get_object(instructions, 'TimelineAddEntries')
        if instruction is None:
            print('[!] can not find valid TimelineAddEntries instruction for %s' % self.username)
            return False

        entries: list = instruction['entries']

        pin_instruction = utils.get_object(instructions, 'TimelinePinEntry')
        if pin_instruction is not None:
            entries.append(pin_instruction['entry'])
        #print('[.] getting %d tweets for %s. we have archived %d tweets' % (len(tweets), self.username, len(self.tweets_json) if archived else 0))

        cleaned_entries = []

        # remove entries we don't need & get cursor if we need
        for entry in entries:
            entry_type = entry['content']['entryType']
            if entry_type == 'TimelineTimelineModule':
                continue
            if entry_type == 'TimelineTimelineCursor':
                if remaining != 0 and entry['content']['cursorType'] == "Bottom":
                    cursor_value = entry['content']['value']
                continue
            cleaned_entries.append(entry)

        tweets += cleaned_entries

        statuses_count = remaining

    v3_ids = set()
    for tweet in tweets:
        entry_id_type = tweet['entryId'].split('-', 1)[0]
        v3_ids.add(entry_id_type)

    for tweet_id in t.tweets_json:
        if tweet_id not in v3_ids:
            print('[.] found missing tweet (%s) for user (%s)' % (tweet_id, username))
            tweet = t.tweets_json[tweet_id]
            fake = create_fake_v3(tweet_id, tweet)
            tweets.append(fake)
            v3_ids.add(tweet_id)

    with open(t.tweets_json_filename, 'w') as outfile:
        json.dump(tweets, outfile)
        #print('[√] refreshed tweets json for %s' % self.username)

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
        u = User(dir, api)
        u._change_parent_dir(data_dir)
        if u.archive():
            print('[.] converting %s...' % dir)
            convert(dir, api)
        else:
            print('[!] failed to archive user.json for %s' % dir)
