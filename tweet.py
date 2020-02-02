from os import path, mkdir, rename, remove
import twint
import sqlite3

class tweet(object):
    def __init__(self, username : str):
        self.username = username
        self.dbname = "database\\%s.db" % self.username

    def archive(self):
        # store to db
        c = twint.Config()
        c.Username = self.username
        c.User_full = True
        c.Hide_output = True
        c.Database = self.dbname
        
        try:
            twint.run.Search(c)
        except sqlite3.OperationalError:
            print("DB Error")
        except:
            print("Error")
        else:
            print("[√] finished downloading all tweets from %s" % self.username)