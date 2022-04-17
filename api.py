from calendar import c
from urllib import response
from xmlrpc.client import Boolean
import requests, json
from bearer_auth import BearerAuth

from datetime import datetime

GUEST_TOKEN_URL = 'https://api.twitter.com/1.1/guest/activate.json'
TWEETS_COUNT = 300 # I think this is a safe count but you may increase. 

class TwitterAPI(object):
    def __init__(self, graphql_ubs: str, graphql_ut: str, graphql_td: str, bearer_token: str):
        self.bearer_token = bearer_token
        self.screen_name_url = 'https://twitter.com/i/api/graphql/%s/UserByScreenName' % graphql_ubs
        self.user_tweets_url = 'https://twitter.com/i/api/graphql/%s/UserTweets' % graphql_ut
        self.tweet_detail_url = 'https://twitter.com/i/api/graphql/%s/TweetDetail' % graphql_td
        self.guest_token = ''

    def get_guest_token(self) -> bool:
        resp = requests.post(GUEST_TOKEN_URL, auth=BearerAuth(self.bearer_token))
        if resp.status_code != 200:
            print('[!] failed to retrive guest token: %d' % resp.status_code)
            return False
        
        if len(resp.text) <= 0:
            print('[!] invalid response retriving guest token: %s' % resp.text)
            return False

        data = json.loads(resp.text)

        if 'guest_token' not in data:
            print('[!] invalid response retriving guest token: %s' % resp.text)
            return False

        self.guest_token = data['guest_token']
        return True

    def get_user_by_screen_name(self, username: str) -> requests.Response:
        variables = '{"screen_name":"%s","withSafetyModeUserFields":false,"withSuperFollowsUserFields":false}' % username
        params = {'variables': variables}
        return requests.get(self.screen_name_url, auth=BearerAuth(self.bearer_token), headers={'x-guest-token': self.guest_token}, params=params)

    def get_tweets(self, rest_id: str, count: int, cursor: str) -> tuple:
        remaining_count = 0
        if count > TWEETS_COUNT:
            remaining_count = count - TWEETS_COUNT
            count = TWEETS_COUNT
        variables = {
            "userId": rest_id,
            "count": count,
            "includePromotedContent": False,
            "withQuickPromoteEligibilityTweetFields": False,
            "withSuperFollowsUserFields": False,
            "withDownvotePerspective": False,
            "withReactionsMetadata": False,
            "withReactionsPerspective": False,
            "withSuperFollowsTweetFields": True,
            "withVoice": True,
            "withV2Timeline": False,
            "__fs_responsive_web_uc_gql_enabled": False,
            "__fs_dont_mention_me_view_api_enabled": False,
            "__fs_interactive_text": False
        }
        if cursor != "":
            variables["cursor"] = cursor
        params = {'variables': json.dumps(variables)}
        resp = requests.get(self.user_tweets_url, auth=BearerAuth(self.bearer_token), headers={'x-guest-token': self.guest_token}, params=params)

        if resp.status_code == 429:
            self.get_guest_token()
            return self.get_tweets(rest_id, count, cursor)

        return (resp, remaining_count)

    def get_tweet(self, rest_id: str) -> requests.Response:
        variables = {
            "focalTweetId": rest_id,
            "with_rux_injections": False,
            "includePromotedContent": False,
            "withCommunity": True,
            "withQuickPromoteEligibilityTweetFields": False,
            "withBirdwatchNotes": False,
            "withSuperFollowsUserFields": False,
            "withDownvotePerspective": False,
            "withReactionsMetadata": False,
            "withReactionsPerspective": False,
            "withSuperFollowsTweetFields": True,
            "withVoice": True,
            "withV2Timeline": False,
            "__fs_responsive_web_uc_gql_enabled": False,
            "__fs_dont_mention_me_view_api_enabled": False,
            "__fs_interactive_text": False
        }

        params = {'variables': json.dumps(variables)}
        resp = requests.get(self.tweet_detail_url, auth=BearerAuth(self.bearer_token), headers={'x-guest-token': self.guest_token}, params=params)

        if resp.status_code == 429:
            self.get_guest_token()
            return self.get_tweet(rest_id)

        return resp
