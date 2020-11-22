from os import path, mkdir
from base import Base
from user import User
from tweets import Tweets
from media import Media

class Account(Base):
    def __init__(self, username : str):
        Base.__init__(self, username)

        # check and create directory
        if not path.exists(self.media_dir):
            mkdir(self.media_dir)

    def archive(self):
        if User(self.username).archive():
            Tweets(self.username).archive()
            Media(self.username).archive()
