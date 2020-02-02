from os import path, mkdir, chdir
from threading import Thread
from queue import Queue

from account import account

# Numbers of downloading threads concurrently
THREADS = 20

class DownloadWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            site = self.queue.get()
            account(site).archive()
            self.queue.task_done()

class ArchiveScheduler(object):
    def __init__(self, sites : list):
        self.sites = sites
        self.queue = Queue()

        # change current working directory to /data/
        if not path.exists("data"):
            mkdir("data")
        
        chdir("data")

        self.scheduling()

    def scheduling(self):
        # create workers
        for _ in range(min(THREADS, len(self.sites))):
            worker = DownloadWorker(self.queue)
            worker.daemon = True
            worker.start()

        # add sites to queue
        for site in self.sites:
            self.queue.put(site)

        self.queue.join()
        print("[√] finished downloading all content")

# borrowed from dixudx/tumblr-crawler
def parse_sites(filename : str):
    with open(filename, "r") as f:
        raw_sites = f.read().rstrip().lstrip()

    raw_sites = raw_sites.replace("\t", ",") \
                         .replace("\r", ",") \
                         .replace("\n", ",") \
                         .replace(" ", ",")
    raw_sites = raw_sites.split(",")

    sites = []
    for raw_site in raw_sites:
        site = raw_site.lstrip().rstrip()
        if site:
            sites.append(site)
    return sites

if __name__ == "__main__":
    cur_dir = path.dirname(path.realpath(__file__))
    sites = None
    
    filename = path.join(cur_dir, "sites.txt")
    if path.exists(filename):
        sites = parse_sites(filename)
    
    if sites:
        ArchiveScheduler(sites)

