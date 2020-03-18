from os import path, mkdir, chdir
from threading import Thread
from queue import Queue
import asyncio

from account import account

class ArchiveScheduler(object):
    def __init__(self, sites : list):
        self.sites = sites

        # change current working directory to /data/
        if not path.exists("data"):
            mkdir("data")
        
        chdir("data")

        self.scheduling()

    def scheduling(self):
        # add sites to queue
        for site in self.sites:
            account(site).archive()

        print("[√] finished downloading all content")

# borrowed from dixudx/tumblr-crawler
def parse_sites(filename : str) -> list:
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
    return list(set(sites))
    
if __name__ == "__main__":
    cur_dir = path.dirname(path.realpath(__file__))
    sites = None
    
    filename = path.join(cur_dir, "sites.txt")
    if path.exists(filename):
        sites = parse_sites(filename)
    
    if sites:
        ArchiveScheduler(sites)

