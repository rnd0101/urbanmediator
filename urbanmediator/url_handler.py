# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Helper functions for handling URLs
"""

import urllib, urlparse, time, datetime, os, sys, urllib2

from util import request_digest, dbg

import config
from config import file_storage

TIMEOUT = 30
AGED = 3600*24  # seconds
CACHE_DIR = "CACHE/"

package_dir = os.path.dirname(config.__file__)
AGENT_PATH = os.path.join(package_dir, "read_feed.py")
READ_FEED_COMMAND = sys.executable + " " + AGENT_PATH

def needToReloadURL(url, cache_dir=CACHE_DIR, aged=AGED):
    req_dig_key = cache_dir + request_digest(url)
    req_dig_md_key = file_storage.metadata(req_dig_key)
    try:
        md = file_storage.getItem(req_dig_md_key)
        if datetime.datetime.now() - md["datetime"] \
	   <= datetime.timedelta(seconds=aged):
            return False
    except StandardError:  # misc errors
        pass
    return True

def tryCachedURL(url, cache_dir=CACHE_DIR, aged=AGED):
    if not needToReloadURL(url, cache_dir, aged):
        req_dig_key = cache_dir + request_digest(url)
        return file_storage.getItem(req_dig_key, mode="file")
    return None

def loadURL(url, cache_dir=CACHE_DIR, aged=AGED, timeout=TIMEOUT):

    #!!! new feature
    cached_result = tryCachedURL(url, cache_dir=CACHE_DIR, aged=aged)
    if cached_result is not None:
        return cached_result

    CMD = READ_FEED_COMMAND + " %s %s %s" % (cache_dir, aged, timeout)
    child_stdin = os.popen(CMD, "w")
    child_stdin.write(url)
    child_stdin.close()

    req_dig_key = cache_dir + request_digest(url)
    return file_storage.getItem(req_dig_key, mode="file")

def loadURL_2(url, cache_dir=CACHE_DIR, aged=AGED, timeout=TIMEOUT):

    CMD = READ_FEED_COMMAND + " %s %s %s" % (cache_dir, aged, timeout)
    child_stdin = os.popen(CMD, "w")
    child_stdin.write(url)
    child_stdin.close()

    req_dig_key = cache_dir + request_digest(url)
    return file_storage.getItem(req_dig_key, mode="file")

def _doRead(url):
    uo = urllib2.urlopen(url)
    return uo.headers.items(), uo

def doLoadURLFast(url, cache_dir=CACHE_DIR, aged=AGED, timeout=TIMEOUT):
    headers, fh = _doRead(url)
    req_dig_key = cache_dir + request_digest(url)
    req_dig_md_key = file_storage.metadata(req_dig_key)

    file_storage.setItem(req_dig_key, fh)
    file_storage.setItem(req_dig_md_key, {"datetime": datetime.datetime.now(), 
                                          "headers": headers})

    return headers, file_storage.getItem(req_dig_key, mode="file")

def getHeaders(url, cache_dir=CACHE_DIR):
    req_dig_key = cache_dir + request_digest(url)
    req_dig_md_key = file_storage.metadata(req_dig_key)
    md = file_storage.getItem(req_dig_md_key)
    return md["headers"]

def loadParsedURL(url):
    req_dig_key = CACHE_DIR + request_digest(url)
    req_dig_md_key = file_storage.metadata(req_dig_key)
    try:
        md = file_storage.getItem(req_dig_md_key)
        if datetime.datetime.now() - md["datetime"] \
	   <= datetime.timedelta(seconds=AGED):
            return md["parsed"]
    except StandardError:  # misc errors
        pass
    return None

def storeParsedURL(url, parsed_data):
    req_dig_key = CACHE_DIR + request_digest(url)
    req_dig_md_key = file_storage.metadata(req_dig_key)

    try:    
        file_storage.setItem(req_dig_md_key, 
                         {"datetime": datetime.datetime.now(),
			  "parsed": parsed_data})  #!!! is pickle fails?
        return True
    except:
        try:    
            file_storage.setItem(req_dig_md_key, 
                {"datetime": datetime.datetime.now(),}
                                )
        except:
            pass
    return False

def loadURL2(url=None, cache_dir=CACHE_DIR, aged=AGED, timeout=TIMEOUT):
    req_dig = request_digest(url)
    req_dig_key = cache_dir + req_dig
    req_dig_md_key = file_storage.metadata(req_dig_key)
    aged_in_cache = False
    in_cache = False
    now = datetime.datetime.now()
    try:
        md = file_storage.getItem(req_dig_md_key)
        in_cache = True
        if aged is not None and \
              now - md["datetime"] > datetime.timedelta(seconds=aged):
            aged_in_cache = True
    except:
        pass

    if in_cache and (config.offline_mode or not aged_in_cache):
        try:
            try:
                headers = dict(file_storage.getItem(req_dig_md_key)["headers"])
            except:
                headers = {'content-type': "application/octet-stream"}
            return headers, file_storage.getItem(req_dig_key, mode="file")
        except:
            file_storage.delItem(req_dig_md_key)
            in_cache = False

    fh = loadURL_2(url, cache_dir=cache_dir, aged=aged, timeout=timeout)

    try:
        headers = dict(file_storage.getItem(req_dig_md_key)["headers"])
    except:
        headers = {'content-type': "application/octet-stream"}

    return headers, fh


def loadURLFast(url=None, cache_dir=CACHE_DIR, aged=AGED, timeout=TIMEOUT):
    req_dig = request_digest(url)
    req_dig_key = cache_dir + req_dig
    req_dig_md_key = file_storage.metadata(req_dig_key)
    aged_in_cache = False
    in_cache = False
    now = datetime.datetime.now()
    try:
        md = file_storage.getItem(req_dig_md_key)
        in_cache = True
        if aged is not None and \
              now - md["datetime"] > datetime.timedelta(seconds=aged):
            aged_in_cache = True
    except:
        pass

    if in_cache and (config.offline_mode or not aged_in_cache):
        try:
            try:
                headers = dict(file_storage.getItem(req_dig_md_key)["headers"])
            except:
                headers = {'content-type': "application/octet-stream"}
            return headers, file_storage.getItem(req_dig_key, mode="file")
        except:
            file_storage.delItem(req_dig_md_key)
            in_cache = False

    headers, fh = doLoadURLFast(url, cache_dir=cache_dir, aged=aged, timeout=timeout)
    try:
        headers = dict(file_storage.getItem(req_dig_md_key)["headers"])
    except:
        headers = {'content-type': "application/octet-stream"}
    return headers, fh

def translate_path(urlpath):
    """Translate a slash-separated urlpath 
    to the local filename syntax.
    """
    return urllib.unquote(urlparse.urlparse(urlpath)[2])
