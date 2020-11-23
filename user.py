import requests
import json

from base import Base
from api import TwitterAPI
import media_downloader as downloader

# allocate the user info in json
class User(Base):
    def __init__(self, username: str, api: TwitterAPI):
        Base.__init__(self, username, api)

    # always replace with new json
    def archive(self) -> bool:
        resp = self.api.get_user_by_screen_name(self.username)
        
        if resp.status_code != 200:
            print('[!] unable to get user object for %s: status code %d' % (self.username, resp.status_code))
            return False
        
        if len(resp.text) <= 0:
            print('[!] invalid response for %s: %s' % (self.username, resp.text))
            return False

        data = json.loads(resp.text)

        if 'errors' in data:
            print('[!] errors in response for %s: %s' % (self.username, data['errors']))
            return False

        if 'data' not in data or 'user' not in data['data'] or 'legacy' not in data['data']['user']:
            print('[!] invalid json response for %s: %s' % (self.username, resp.text))
            return False
            
        user_json = data['data']['user']

        if user_json['legacy']['protected'] is True:
            print('[!] %s profile is protected' % self.username)
            return False

        # download avatar
        avatar_image_url = user_json['legacy']['profile_image_url_https']
        # remove '_normal' to get the hi-res one
        avatar_image_url = avatar_image_url.replace('_normal', '')
        downloader.avatar_photo(avatar_image_url, self.media_dir)

        # download banner. some user does not have picture banner but instead has colored background
        if 'profile_banner_url' in user_json['legacy']:
            banner_image_url = user_json['legacy']['profile_banner_url']
            downloader.banner_photo(banner_image_url, self.media_dir)

        with open(self.user_json_filename, 'w') as outfile:
            json.dump(user_json, outfile)
            #print('[√] refreshed user json for %s' % self.username)
            return True

        print('[!] failed to open file `%s` for %s' % (self.user_json_filename, self.username))
        return False
