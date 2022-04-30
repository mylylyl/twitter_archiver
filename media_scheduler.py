import queue
from threading import Thread
from queue import Queue
from enum import Enum

import media_downloader as downloader

class MediaType(Enum):
    VIDEO = 1
    PHOTO = 2

class MediaInfo:
    def __init__(self, type: MediaType, url: str, download_dir: str, source_video_id: str):
        self.type = type
        self.url = url
        self.download_dir = download_dir
        self.source_video_id = source_video_id # to get the real id of retweeted videos

class MediaWorker(Thread):
    def __init__(self, queue: Queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            mi: MediaInfo = self.queue.get()
            if mi.type == MediaType.VIDEO:
                downloader.video(mi.url, mi.source_video_id, mi.download_dir)
            elif mi.type == MediaType.PHOTO:
                downloader.tweet_photo(mi.url, mi.download_dir)
            self.queue.task_done()

class MediaScheduler(object):
    def __init__(self):
        self.queue = Queue()

    def start_workers(self, threads: int):
        for _ in range(threads):
            worker = MediaWorker(self.queue)
            worker.daemon = True
            worker.start()
