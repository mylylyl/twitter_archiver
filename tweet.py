from os import path, mkdir, rename, remove
import twint
import sqlite3

class tweet(object):
    def __init__(self, username : str):
        self.username = username
        self.dbname = self.username + ".db"

    def archive(self):
        # move the db to cwd if exists
        if path.exists("db\\" + self.dbname) and not path.exists(self.dbname):
            rename("db\\" + self.dbname, self.dbname)
        # store tweets
        self.store_tweets()
        # move to db folder
        if path.exists("db\\" + self.dbname):
            remove("db\\" + self.dbname)
        rename(self.dbname, "db\\" + self.dbname)

    def store_tweets(self):
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