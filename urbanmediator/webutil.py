# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Useful utility functions. Dependent on the web.py and config.py

"""

import rfc822, time, urllib, urlparse, re, cgi

import web
import web.utils

import config

def request_uri(prefix=""):
    """ Current request """
    query_string = web.ctx.environ["QUERY_STRING"]
    path_info = web.ctx.environ["PATH_INFO"]
    query_string = query_string and ("?" + query_string)
    return config.base_url + prefix + path_info + query_string

def set_last_modified(t):
    """ t - datetime
    """
    web.header('Last-Modified', 
        rfc822.formatdate(
            time.mktime(t.timetuple())+1e-6*t.microsecond)
        )

def dictify(fs): return dict([(k, fs[k]) for k in fs.keys()])

def get_query(url):
    _d, _d, path, _d, query, fragment = urlparse.urlparse(url)
    return web.utils.storify(dictify(cgi.FieldStorage(
        environ=dict(QUERY_STRING=query), 
        keep_blank_values=1)))

_d, _d, base_path, _d, _d, _d = urlparse.urlparse(config.base_url)

def dispatch_url(urlpath, modvars, mapping, prefix="/widget"):
    """
    Based on handle in web.py's request.py 
    Simplified to work only for the current module.
    """

    _d, _d, path, _d, query, fragment = urlparse.urlparse(urlpath)

    path = web.lstrips(path, base_path)

    for url, ofn in web.utils.group(mapping, 2):
        fn, result = web.utils.re_subm('^' + prefix + url + '$', ofn, path)
        if result:
            try:
                cls = modvars[fn]
            except KeyError: 
                return "[ERROR 1]"
            
            meth = "GET"
            if not hasattr(cls, meth): 
                return "[ERROR 2]"
            tocall = getattr(cls(), meth)
            args = list(result.groups())
            for d in re.findall(r'\\(\d+)', ofn):
                args.pop(int(d) - 1)

            query = get_query(urlpath)

            return tocall(*([x and urllib.unquote(x) for x in args]), 
                 **{'onlycode': True, 
                    'webinput': query}
            )
    return "[ERROR 3]"

