from tweet import tweet
from media import media

class account:
    def __init__(self, username : str):
        self.username = username
        self.tweet_manager = tweet(self.username)
        self.media_manager = media(self.username)

    def archive(self):
        self.tweet_manager.archive()
        self.media_manager.archive()