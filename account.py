from os import path, mkdir

from base import Base
from user import User
from tweets import Tweets
from media import Media
from api import TwitterAPI

class Account(Base):
    def __init__(self, username: str, api: TwitterAPI):
        Base.__init__(self, username, api)

    def archive(self):
        # check and create directory
        if not path.exists(self.media_dir):
            mkdir(self.media_dir)
        
        if User(self.username, self.api).archive():
            Tweets(self.username, self.api).archive()
            Media(self.username, self.api).archive()
