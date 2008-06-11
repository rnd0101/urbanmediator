# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Utility functions independent from web.py or config.
"""

import re, datetime, sys, os, sha, cgi, urllib, urlparse
import rfc822, time
import feedparser

date_fullyear = "([0-9]{4})"
date_month = "(0[0-9]|1[012])"
date_mday = "([0123][0-9])"
time_hour = "([012][0-9])"
time_minute = "([0-6][0-9])"
time_secondfrac = "([0-6][0-9](?:[.][0-9]+)?)"
time_numoffset = "[+-]" + time_hour + ":" + time_minute
time_offset = "([Zz]|"+ time_numoffset + ")"
partial_time = time_hour + ":" + time_minute + ":" + time_secondfrac
full_date = date_fullyear + "-" + date_month + "-" + date_mday
full_time = partial_time + time_offset
date_time = full_date + "[Tt]" + full_time

datetime_re = re.compile(date_time)

def now():
    return datetime.datetime.now()

def parse_rfc3339_date(datestr):
    # !!! tz assumed 'Z'
    try:
        parsed = datetime_re.match(datestr).groups()
        return datetime.datetime(*map(int, parsed[:6]))
    except:
        raise
        return now()

def parse_qs(qs):
    return cgi.parse_qs(qs)

def request_digest(url):
    return sha.new(url).hexdigest()

def entry_digest(d):
    return sha.new(repr(d)).hexdigest()

def loc_digest(location):
    try:  # new way
        return "L-" + request_digest(location.uuid)
    except:  # old way
        return request_digest("%s-%s"% (location.id, location.url))

class EntityMixin:
    """ This is to mixin Entity interface
    """
    def __getattr__(self, key): 
        try: return self[key]
        except KeyError, k: raise AttributeError, k
    def __setattr__(self, key, value): self[key] = value
    def __delattr__(self, key):
        try: del self[key]
        except KeyError, k: raise AttributeError, k


class Entity(dict):
    """ This is replica of web.utils.Storage changed for
    representing data object in the model
    """
    def __getattr__(self, key): 
        try: return self[key]
        except KeyError, k: raise AttributeError, k
    def __setattr__(self, key, value): self[key] = value
    def __delattr__(self, key):
        try: del self[key]
        except KeyError, k: raise AttributeError, k
    def __repr__(self):
        return self.__class__.__name__ + "(" + dict.__repr__(self) + ")"


class Links(Entity):
    """ This is for smart link representation
    """

    def __call__(self, key_, *args, **kwargs):
        main_url = self.get(key_)
        dict_args = dictmerge(*[a for a in args if hasattr(a, "has_key")], **kwargs)
        pos_args = [a for a in args if not hasattr(a, "has_key")]

        if main_url is None:
            raise ValueError, "No such link"

        if "%s" in main_url:
            # if we have format string
            main_url = main_url % tuple(pos_args)
        else:
            # legacy: if we do not have format string, just add at the end
            if pos_args:
                main_url = main_url.rstrip("/") + "/" + str(pos_args[0])
        query = dict_args and ("?" + urllib.urlencode(dict_args)) or ""
        return main_url + query
    



def normalize_url(url, to_del=''):
    parsed = list(urlparse.urlparse(url))
    query = "&" + parsed[-2].replace("&amp;", "&")
    to_del_re = re.compile("("+"|".join(
        [("[&]%s=[^&]+" % i) for i in to_del.split()]
        ) +")")
    parsed[-2] = to_del_re.sub("", query).lstrip("&")
    newurl = urlparse.ParseResult(*parsed)
    return newurl.geturl()

def normalize_url(url, to_del=''):
    # hackish variant for Python 2.4
    try:
        url1, query = url.split("?", 1)
    except:
        return url
    query = "&" + query.replace("&amp;", "&")
    to_del_re = re.compile("("+"|".join(
        [("[&]%s=[^&]+" % i) for i in to_del.split()]
        ) +")")
    query = to_del_re.sub("", query).lstrip("&")
    return url1 + "?" + query

def sanitize_html(html):
    return html
    return feedparser._sanitizeHTML(html, 'utf-8')

NOT_SID_RE = "[^_0-9a-zA-Z]"
def sanitize_session_id(sid):
    return re.sub(NOT_SID_RE, "", sid)


def dictclean(d):
    for k, v in d.items():
        if v is None:
            del d[k]

def dictclean2(d):
    for k, v in d.items():
        if v is None or v == '':
            del d[k]


def dictmerge(*dicts, **singles):
    res = Entity()
    for d in dicts:
        res.update(d)
    res.update(singles)
    dictclean(res)
    return res

def pagination_numbers(current, all, radius=2, border=1):
    """ 1 ... 5 6 7 8 9 ... 20 """
    maxlen = (border + radius) * 2 + 3
    if all <= maxlen:
        return range(1, all+1)
    rawpages = list(set(range(1, all+1)) & \
        (set(range(1, border+1)) | set(range(all-border+1, all+1)) \
            | set(range(current-radius, current+radius+1))))
    rawpages.sort()

    pages = []
    for (a1, a2) in zip(rawpages, [0]+rawpages):
        if a1 - a2 != 1:
            pages.append(0)   # 0 - "..."
        pages.append(a1) 
    return pages

def defaultizer(storage, source={}, default={}):
    """
    Updates `storage` according to `defaults`,
    first from `source` (if available), then from `default` itself.
    Thus, `default` can be seen as scheme.
    """
    for (k, v) in default.items():
        storage.setdefault(k, source.get(k, v))


comments_re = re.compile('<!--.*?-->', re.M)
tags_re = re.compile('<.*?>', re.M)
blanks_re = re.compile('\s+|[&]nbsp[;]', re.M)

def first_line(s, length=100):
    """ Get the first line of text from HTML
    """
    s = s.replace('\n', ' ')
    s = comments_re.sub('', s)
    s = tags_re.sub('', s)
    s = blanks_re.sub(' ', s)
    if len(s) <= length:
        return s

    s1 = ""
    for frag in s.split():
        if len(s1) + len(frag) > length:
            break
        s1 += " " + frag
    return s1 + " ..."

class SimpleTimer:
    def __init__(self, label=None):
        self._t = []
        self._l = []
        self.P(label)

    def P(self, label=None):
        self._t.append(time.time())
        self._l.append(label or ("%i" % len(self._l)))

    def R(self, label=None):
        self.P(label)
        result = "TOTAL: %2.4f" % (self._t[-1] - self._t[0])
        for i in enumerate(zip(self._l, self._t)):
            if i[0] > 0:
                result += """, %s-%s: %2.4f s""" % (self._l[i[0]-1], i[1][0], i[1][1] - self._t[i[0]-1])
        return result


def dbg(*args, **kwargs):
    import sys
    print >> sys.stderr, "*"*70
    for a in args:
        print >> sys.stderr, a,
    print >> sys.stderr
    for k, v in kwargs.items():
        print >> sys.stderr, k, "=", v

def print_js(s):
    printed = ""
    if isinstance(s, dict):
        printed += "{"
        printed += ", ".join(['"%s": %s' % (k, print_js(v)) for k, v in s.items()])
        printed += "}"
    elif isinstance(s, list):
        printed += "["
        printed += ", ".join([print_js(v) for v in s])
        printed += "]"
    elif isinstance(s, str):
        printed += '"%s"' % s.replace("/", "\/")
    elif isinstance(s, int):
        printed += str(s)
    elif isinstance(s, long):
        printed += str(s)
    return printed


import re, htmlentitydefs

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
# source: http://effbot.org/zone/re-sub.htm#unescape-html

def unescape_refs(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text).encode("utf-8")

def parse_qs(url):
    return cgi.parse_qs(urlparse.urlparse(url)[4])
