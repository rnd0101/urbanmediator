# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Script used to fetch data given URL and timeout.

    !!! UM config not used for this one.
    Config done below. Should have exact same values as main config.
"""

import signal, time, sys, os, sha, datetime
from urllib2 import urlopen

from DocStorage import FSStorage

########################## Config 
# storing files
STORAGE_DIR = os.environ["HOME"] + "/.urban_mediator"
file_storage = FSStorage("file://" + STORAGE_DIR, STORAGE_DIR)
#
# XXX !!! move to config
##########################

def request_digest(url):
    return sha.new(url).hexdigest()

# !!! move to config
TIMEOUT = 25    # default timeout, seconds
AGED = 3600*24  # default aging threshold, seconds

#from ACPN Python cookbook

class TimedOutExc(Exception):
    def __init__(self, value = "Timed Out"):
        self.value = value
    def __str__(self):
        return repr(self.value)

def TimedOutFn(f, timeout, *args, **kwargs):
    def handler(signum, frame):
        raise TimedOutExc()
    
    old = signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)
    try:
        result = f(*args, **kwargs)
    finally:
        signal.signal(signal.SIGALRM, old)
    signal.alarm(0)
    return result


def timed_out(timeout):
    def decorate(f):
        def handler(signum, frame):
            raise TimedOutExc()
        
        def new_f(*args, **kwargs):
            old = signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)
            try:
                result = f(*args, **kwargs)
            finally:
                signal.signal(signal.SIGALRM, old)
            signal.alarm(0)
            return result
        
        new_f.func_name = f.func_name
        return new_f

    return decorate

def _doReadFeed(url):
    uo = urlopen(url)
    return uo.headers.items(), uo

def readFeed(url=None, cache_dir="CACHE/", aged=AGED, custom_timeout=None):
    req_dig = request_digest(url)
    req_dig_key = cache_dir + req_dig
    req_dig_md_key = file_storage.metadata(req_dig_key)
    custom_timeout = custom_timeout or TIMEOUT
    aged_in_cache = False
    in_cache = False
    now = datetime.datetime.now()
    try:
        md = file_storage.getItem(req_dig_md_key)
        in_cache = True
        if now - md["datetime"] > datetime.timedelta(seconds=aged):
            aged_in_cache = True
    except:
        pass

    if in_cache and not aged_in_cache:
        try:
            return file_storage.getItem(req_dig_key, mode="file")
        except:
            file_storage.delItem(req_dig_md_key)
            in_cache = False

    try:
        headers, data = timed_out(custom_timeout)(_doReadFeed)(url)

        file_storage.setItem(req_dig_md_key, {"datetime": now, 
                                              "headers": headers})
        file_storage.setItem(req_dig_key, data)
    except:
        raise
        if aged_in_cache:
            return file_storage.getItem(req_dig_key, mode="file")
        return "None"

    return file_storage.getItem(req_dig_key, mode="file")


# Its safe to read stdin instead of having URL in arguments list

try:
    cache_dir = sys.argv[1]
except:
    cache_dir = "CACHE/"

try:
    aged = sys.argv[2]
    if aged == "None":
        aged = None
    else:
        aged = int(aged)
except:
    aged = AGED

try:
    custom_timeout = sys.argv[3]
    if custom_timeout == "None":
        custom_timeout = None
    else:
        custom_timeout = int(custom_timeout)
except:
    custom_timeout = TIMEOUT

url = sys.stdin.read().strip()
t1 = time.time()
data = readFeed(url, cache_dir=cache_dir, aged=aged, custom_timeout=custom_timeout)
# sys.stdout.write(data.read())
