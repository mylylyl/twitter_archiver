import sqlite3
from os import path, mkdir
import media_downloader as downloader

class media(object):
    def __init__(self, username : str):
        self.username = username
        # media\\username
        self.media_dir = "media\\" + self.username
        if not path.exists(self.media_dir):
            mkdir(self.media_dir)
        
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
        rows = self.cur_t.execute("SELECT photos, id FROM tweets ORDER BY created_at")
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
        name_diff = list(set(list(ops.difference(nks)) + list(nks.difference(ops))))
        if not name_diff:
            return
        for name in name_diff:
            self.cur.execute("INSERT INTO photo (name, id, downloaded) VALUES ('%s', %d, 0)" % (name, name_dict[name]))
        self.conn.commit()
        print("[+] found %d new photos" % len(name_diff))

    def get_photos_to_be_download(self) -> list(str):
        photos_to_be_download = []
        rows = self.cur.execute("SELECT name FROM photo WHERE downloaded = 0")
        for row in rows:
            photos_to_be_download.append(row[0])
        return photos_to_be_download

    def set_photos_downloaded(self, photos):
        for photo_name in photos:
            self.cur.execute("UPDATE photo SET downloaded = 1 WHERE name = '%s'" % photo_name)
        self.conn.commit()

    def download_photos(self):
        self.populate_photos()
        photos = self.get_photos_to_be_download()
        if photos:
            print("[+] %d photos to be downloaded" % len(photos))
            for photo_name in photos:
                downloader.photo(photo_name, self.media_dir)
            self.set_photos_downloaded(photos)
        print("[√] finished downloading all photos")

    def populate_videos(self):
        # populate tweet ids into db
        all_vid_ids = []
        rows = self.cur_t.execute("SELECT id FROM tweets WHERE video = 1 ORDER BY created_at")
        for row in rows:
            all_vid_ids.append(row[0])
        old_vid_ids = []
        rows = self.cur.execute("SELECT id FROM video")
        for row in rows:
            old_vid_ids.append(row[0])
        avi = set(all_vid_ids)
        ovi = set(old_vid_ids)
        vid_diff = list(set(list(avi.difference(ovi)) + list(ovi.difference(avi))))
        if not vid_diff:
            return
        for vid in vid_diff:
            self.cur.execute("INSERT INTO video (id, downloaded) VALUES (%d, 0)" % vid)
        self.conn.commit()
        print("[+] found %d new videos" % len(vid_diff))

    def get_videos_to_be_download(self) -> list(str):
        videos_to_be_download = []
        rows = self.cur.execute("SELECT id FROM video WHERE downloaded = 0")
        for row in rows:
            videos_to_be_download.append(row[0])
        return videos_to_be_download

    def set_videos_downloaded(self, videos):
        for video_id in videos:
            self.cur.execute("UPDATE video SET downloaded = 1 WHERE id = %d" % video_id)
        self.conn.commit()

    def download_videos(self):
        self.populate_videos()
        videos = self.get_videos_to_be_download()
        if videos:
            print("[+] %d videos to be downloaded" % len(videos))
            for video_id in videos:
                downloader.video(video_id, self.media_dir)
            self.set_videos_downloaded(videos)
        print("[√] finished downloading all videos")

    def archive(self):
        self.download_photos()
        self.download_videos()

    def __del__(self):
        self.conn.close()
        self.conn_t.close()

