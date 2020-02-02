from os import path, mkdir, rename, remove
import sys
import sqlite3
import asyncio

import twint

class tweet(object):
    def __init__(self, username : str):
        self.username = username
        self.dbname = "%s\\tweet.db" % self.username

    def archive(self):
        # use twint in multithread env
        asyncio.set_event_loop(asyncio.new_event_loop())
        
        # store to db
        c = twint.Config()
        c.Username = self.username
        c.User_full = True
        c.Hide_output = True
        c.Database = self.dbname
        
        try:
            twint.run.Search(c)
        except sqlite3.OperationalError:
            print("[x] database error")
            sys.exit(1)
        except RuntimeError:
            print("[x] runtime error: ", sys.exc_info())
        except:
            print("[x] unexpected error: ", sys.exc_info())
            sys.exit(1)
        else:
            print("[√] finished downloading all tweets from %s" % self.username)