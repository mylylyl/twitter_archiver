from ctypes import util
import json
import sys
import requests

from base import Base
from api import TwitterAPI
import utils

class Tweets(Base):
    def __init__(self, username : str, api : TwitterAPI):
        Base.__init__(self, username, api)

    def archive(self) -> bool:
        if self._read_user_json() is False:
            #print('[!] failed to read user json for %s, skipping archive' % self.username)
            return False

        archived = self._read_tweets_json()
        #if archived is False:
        #    print('[.] %s was not archived before' % self.username)
        #else:
        #    print('[.] %s has %d tweets archived' % (self.username, len(self.tweets_json)))

        print('[.] getting tweets for %s (display_name: %s, follower: %d, following: %d)' % (self.username, self.user_json['legacy']['name'], self.user_json['legacy']['followers_count'], self.user_json['legacy']['friends_count']))

        statuses_count = self.user_json['legacy']['statuses_count']

        tweets = []
        cursor_value = ""

        while statuses_count != 0:
            resp, remaining = self.api.get_tweets(self.user_json['rest_id'], statuses_count, cursor_value)

            if resp.status_code != 200:
                print('[!] unable to get user object for %s: status code %d' % (self.username, resp.status_code))
                return False
            
            if len(resp.text) <= 0:
                print('[!] invalid response for %s: %s' % (self.username, resp.text))
                return False

            data = json.loads(resp.text)

            if 'errors' in data:
                print('[!] errors in tweets json response for %s: %s' % (self.username, data['errors']))
                return False

            if not utils.has_keys(data, ['data', 'user', 'result', 'timeline', 'timeline', 'instructions']):
                print('[!] invalid tweets json response for %s: %s' % (self.username, resp.text))
                return False

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
                if entry_type != 'TimelineTimelineItem':
                    print('[!] unknown entry type %s for %s, id %s' % (entry_type, self.username, entry['entryId']))
                    continue
                item_type = entry['content']['itemContent']['itemType']
                if item_type == 'TimelineTombstone':
                    # tombstone can be age-restricted content. bypass by using TweetDetail api
                    rest_id = entry['entryId'].split('-', 1)[1]
                    sort_id = entry['sortIndex']
                    if rest_id != sort_id:
                        print('[!] entryId different from sortIndex (%s vs %s) of %s: status code %d' % (rest_id, sort_id, self.username, tweet_resp.status_code))
                    tweet_resp = self.api.get_tweet(rest_id)
                    if tweet_resp.status_code != 200:
                        print('[!] unable to get tweet detail for %s of %s: status code %d' % (rest_id, self.username, tweet_resp.status_code))
                        continue
                    if len(tweet_resp.text) <= 0:
                        print('[!] invalid tweet detail response for %s of %s: %s' % (rest_id, self.username, tweet_resp.text))
                        continue
                    tweet_detail = json.loads(tweet_resp.text)
                    if not utils.has_keys(tweet_detail, ['data', 'threaded_conversation_with_injections', 'instructions']):
                        print('[!] invalid tweet detail object for %s of %s: %s' % (rest_id, self.username, tweet_detail))
                        continue
                    td_instructions = tweet_detail['data']['threaded_conversation_with_injections']['instructions']
                    if len(td_instructions) != 2:
                        print('[!] invalid tweet detail instructions count %d for %s of %s: %s' % (len(td_instructions), rest_id, self.username, tweet_detail))
                        continue
                    if len(td_instructions[0]['entries']) == 0:
                        # there could be conversation entries
                        print('[!] invalid tweet detail instructions entries count 0 for %s of %s: %s' % (rest_id, self.username, tweet_detail))
                        continue
                    td_entry = td_instructions[0]['entries'][0]
                    if not utils.has_keys(td_entry, ['content', 'itemContent', 'tweet_results', 'result', '__typename']) or td_entry['content']['itemContent']['tweet_results']['result']['__typename'] != "Tweet":
                        if 'tombstone' in td_entry['entryId']:
                            #FIXME need login to view
                            continue
                        print("[!] invalid td_entry object for %s: %s" % (self.username, td_entry))
                        continue
                    cleaned_entries.append(td_entry)
                    continue
                if item_type != 'TimelineTweet':
                    print('[!] unknown item type %s for %s, id %s' % (item_type, self.username, entry['entryId']))
                    continue
                if not utils.has_keys(entry, ['content', 'itemContent', 'tweet_results', 'result', '__typename']):
                    print("[!] invalid entry object for %s: %s" % (self.username, entry))
                    continue
                type_name = entry['content']['itemContent']['tweet_results']['result']['__typename']
                if type_name == "TweetTombstone":
                    # need to login to twitter?
                    continue
                if type_name != "Tweet":
                    print("[!] invalid type name (%s) for tweet object of %s: %s" % (type_name, self.username, entry))
                    continue
                cleaned_entries.append(entry)

            tweets += cleaned_entries

            statuses_count = remaining
        
        if archived is True:
            # merge the two json so we don't miss deleted ones
            sort_indexes = set()
            for tweet in tweets:
                sort_indexes.add(tweet['entryId'])
            for tweet in self.tweets_json:
                if tweet['entryId'] not in sort_indexes:
                    entry_id_type = tweet['entryId'].split('-', 1)[0]
                    if entry_id_type != "tweet":
                        print('[!] (archived) unknown entry id type %s for %s, id %s' % (entry_id_type, self.username, tweet['entryId']))
                        continue
                    entry_type = tweet['content']['entryType']
                    if entry_type == 'TimelineTimelineModule' or entry_type == 'TimelineTimelineCursor':
                        continue
                    item_type = tweet['content']['itemContent']['itemType']
                    if item_type != 'TimelineTweet':
                        print('[!] (archived) unknown item type %s for %s, id %s' % (item_type, self.username, tweet['entryId']))
                        continue
                    if not utils.has_keys(tweet, ['content', 'itemContent', 'tweet_results', 'result', '__typename']):
                        print("[!] (archived) invalid entry object for %s: %s" % (self.username, tweet))
                        continue
                    type_name = tweet['content']['itemContent']['tweet_results']['result']['__typename']
                    if type_name != "Tweet":
                        print("[!] (archived) invalid type name (%s) for tweet object of %s: %s" % (type_name, self.username, tweet))
                        continue
                    tweets.append(tweet)

        try:
            with open(self.tweets_json_filename, 'w') as outfile:
                json.dump(tweets, outfile)
                #print('[√] refreshed tweets json for %s' % self.username)
                return True
        except:
            print('[!] failed to save tweet json file (%s) for %s' % (self.tweets_json_filename, self.username))
            return False

        
