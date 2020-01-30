import sqlite3
from os import path

PHOTO_BASE_URL = "https://pbs.twimg.com/media/"
VIDEO_BASE_URL = "https://twitter.com/statuses/"

class media(object):
    def __init__(self, username : str):
        self.username = username
        
        # username_media.db
        dbname = self.username + "_media.db"
        if path.exists("db\\" + dbname):
            self.conn = sqlite3.connect("db\\" + dbname)
            self.cur = self.conn.cursor()
        else:
            self.conn = sqlite3.connect("db\\" + dbname)
            self.cur = self.conn.cursor()
            # create table for photos
            self.cur.execute('''CREATE TABLE photo (
                name TEXT PRIMARY KEY,
                id INT NOT NULL,
                downloaded INT NOT NULL DEFAULT 0
                ) WITHOUT ROWID;''')
            # create table for photos
            self.cur.execute('''CREATE TABLE video (
                id INT PRIMARY KEY,
                downloaded INT NOT NULL DEFAULT 0)
                ;''')
            self.conn.commit()

        # load tweet db
        dbname_t = self.username + ".db"
        self.conn_t = sqlite3.connect("db\\" + dbname_t)
        self.cur_t = self.conn_t.cursor()

    def populate_photos(self):
        # populate photo names into db
        # photo name -> id
        name_dict = {}
        rows = self.cur_t.execute("SELECT photos, id FROM tweets")
        for row in rows:
            raw_url = row[0]
            if not raw_url:
                continue
            if "," in raw_url:
                urls = raw_url.split(",")
                for url in urls:
                    photo_name = url[28:43]
                    name_dict[photo_name] = row[1]
            else:
                photo_name = raw_url[28:43]
                name_dict[photo_name] = row[1]
        # fetch photo names from media db
        old_photo_names = []
        rows = self.cur.execute("SELECT name FROM photo")
        for row in rows:
            old_photo_names.append(row[0])
        # get the newly fetched tweets' photo names
        



    def download_videos(self):
        # populate tweet ids into db
        r = self.cur_t.execute("SELECT id FROM tweets")
        for p in r:
            print(p)

    def __del__(self):
        self.conn.close()
        self.conn_t.close()

