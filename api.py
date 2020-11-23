import requests, json
from bearer_auth import BearerAuth

from datetime import datetime

TIMELINE_API_URL = 'https://api.twitter.com/2/timeline/profile/'
GUEST_TOKEN_URL = 'https://api.twitter.com/1.1/guest/activate.json'

class TwitterAPI(object):
    def __init__(self, graphql_endpoint : str, bearer_token : str):
        self.graphql_endpoint = graphql_endpoint
        self.bearer_token = bearer_token
        self.screen_name_url = 'https://api.twitter.com/graphql/%s/UserByScreenName' % self.graphql_endpoint
        self.guest_token = ''

    def _get_guest_token(self) -> bool:
        resp = requests.post(GUEST_TOKEN_URL, auth=BearerAuth(self.bearer_token))
        if resp.status_code == 200:
            token_json = resp.json()
            if 'guest_token' in token_json:
                self.guest_token = token_json['guest_token']
                print('[.] setting guest_token to %s' % self.guest_token)
                return True
        
        return False

    def get_user_by_screen_name(self, username: str) -> requests.Response:
        variables = '{"screen_name":"%s","withHighlightedLabel":true}' % username
        params = {'variables': variables}
        return requests.get(self.screen_name_url, auth=BearerAuth(self.bearer_token), params=params)

    def get_tweets(self, rest_id: str, count: int) -> requests.Response:
        if self.guest_token == '':
            self._get_guest_token()

        timeline_api_url = '%s%s.json' % (TIMELINE_API_URL, rest_id)
        params = {
            'include_profile_interstitial_type': 1,
            'include_blocking': 1,
            'include_blocked_by': 1,
            'include_followed_by': 1,
            'include_want_retweets': 1,
            'include_mute_edge': 1,
            'include_can_dm': 1,
            'include_can_media_tag': 1,
            'skip_status': 1,
            'cards_platform': 'Web-12',
            'include_cards': 1,
            'include_ext_alt_text': 'true',
            'include_quote_count': 'true',
            'include_reply_count': 1,
            'tweet_mode': 'extended',
            'include_entities': 'true',
            'include_user_entities': 'true',
            'include_ext_media_color': 'true',
            'include_ext_media_availability': 'true',
            'send_error_codes': 'true',
            'simple_quoted_tweet': 'true',
            'include_tweet_replies': 'false',
            'ext': 'mediaStats,highlightedLabel',
            'count': count,
        }
        resp = requests.get(timeline_api_url,
                            auth=BearerAuth(self.bearer_token),
                            params=params,
                            headers={'x-guest-token': self.guest_token})

        if resp.status_code == 403:
            if self._get_guest_token():
                return self.get_tweets(rest_id, count)

        return resp
