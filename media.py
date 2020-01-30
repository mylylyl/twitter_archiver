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
        nks = set(name_dict.keys())
        ops = set(old_photo_names)
        diff = list(set(list(ops.difference(nks)) + list(nks.difference(ops))))
        if not diff:
            return
        print("[+] found %d new photos" % len(diff))
        # create tuples then convert to string
        # (id, name, 0)
        values = []
        for d in diff:
            values.append((name_dict[d], d, 0))
        values_str = ','.join([str(value) for value in values])
        self.cur.execute("INSERT INTO photo VALUES " + values_str)
        self.conn.commit()
        print("[√] finished populating new photos")

    def get_photos_to_be_download(self):
        photos_to_be_download = []
        rows = self.cur.execute("SELECT name FROM photo WHERE downloaded = 0")
        for row in rows:
            photos_to_be_download.append(row[0])
        return photos_to_be_download

    def download_photos(self):
        self.populate_photos()
        photos = self.get_photos_to_be_download()
        print("[+] %d photos to be downloaded" % len(photos))
        print("[√] finished downloading all photos")



    def download_videos(self):
        # populate tweet ids into db
        r = self.cur_t.execute("SELECT id FROM tweets")
        for p in r:
            print(p)

    def __del__(self):
        self.conn.close()
        self.conn_t.close()

