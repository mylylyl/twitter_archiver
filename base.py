import sys, json
import pathlib
from api import TwitterAPI

class Base(object):
    def __init__(self, username : str, api : TwitterAPI):
        self.username = username
        self.api = api
        self.parent_dir = 'data'
        self.media_dir = str(pathlib.Path(self.parent_dir, self.username))
        self.user_json_filename = str(pathlib.Path(self.media_dir, 'user.json'))
        self.tweets_json_filename = str(pathlib.Path(self.media_dir, 'tweets.json'))

    def _change_parent_dir(self, dir: str):
        self.parent_dir = dir
        self.media_dir = str(pathlib.Path(self.parent_dir, self.username))
        self.user_json_filename = str(pathlib.Path(self.media_dir, 'user.json'))
        self.tweets_json_filename = str(pathlib.Path(self.media_dir, 'tweets.json'))

    def _read_user_json(self) -> bool:
        try:
            with open(self.user_json_filename, 'r') as f:
                self.user_json = json.load(f)
                return True
        except FileNotFoundError:
            # print('[!] %s file not found' % self.user_json_filename)
            return False
        except AttributeError as error:
            print('[!] attribute error: %s' % error)
            return False
        except:
            print('[!] unexpected error: %s', sys.exc_info()[0])
            return False

        print('[!] unknown error')
        return False

    def _read_tweets_json(self) -> bool:
        try:
            with open(self.tweets_json_filename, 'r') as f:
                self.tweets_json = json.load(f)
                return True
        except FileNotFoundError:
            #print('[!] %s file not found' % self.tweets_json_filename)
            return False
        except AttributeError as error:
            print('[!] attribute error: %s' % error)
            return False
        except:
            print('[!] unexpected error:', sys.exc_info()[0])
            return False

        print('[!] unknown error')
        return False