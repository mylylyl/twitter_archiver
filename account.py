from os import path, mkdir

from tweet import tweet
from media import media

class account:
    def __init__(self, username : str):
        self.username = username

        # check and create directory
        if not path.exists(self.username):
            mkdir(self.username)

    def archive(self):
        tweet(self.username).archive()
        media(self.username).archive()
