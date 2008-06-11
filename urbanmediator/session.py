# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Session handler and related helper functions.
"""

import time, sha, random, datetime

import web
from web.utils import Storage

import util
from webutil import request_uri

import config
from config import file_storage

SESSION_DIR = "SESSIONS/"
COOKIE_NAME = "NEW" + config.session_cookie_name  #!!!

def _timestamp():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def _new_session_id():
    return _timestamp() + "_" + hex(random.randint(1,10**120))[2:-1]

def start(info):
    """ Starts a session. Remember not to redirect after this. """
    session_id = _new_session_id()
    session_key = SESSION_DIR + session_id
    info = Storage(info)
    info.id = session_id
    info.added =  time.time()
    info.referer = web.ctx.environ.get("HTTP_REFERER", "")
    info.entry = request_uri()
    file_storage.setItem(session_key, info)
    web.setcookie(COOKIE_NAME, session_id)
    web.ctx.current_session_id = session_id
    # !!!TODO: session own log? (take care of UM instances with shared fsstorage)
    return info

def get_session_id():
    try:
        return web.ctx.current_session_id
    except:
        try:
            web_cookies = web.cookies()
            web.ctx.current_session_id = session_id = \
                util.sanitize_session_id(
                    web_cookies.get(COOKIE_NAME, None))
            return session_id
        except:
            return None

def get_session():
    """Get existing session (may return None) """
    session_id = get_session_id()
    if session_id is not None:
        session_key = SESSION_DIR + session_id
        try:
            return file_storage.getItem(session_key, mode="pickle")
        except:
            return None
    else:
        return None

def session():
    """Get session or start new one. """
    return get_session() or start({})

def update_info(new_info):
    """Updates session info."""
    session_id = get_session_id()
    session_key = SESSION_DIR + session_id
    info = get_session()
    info.update(new_info)
    info.id = session_id  # this should not change

    file_storage.setItem(session_key, info)
    return info

def remove_info(new_info):
    session_id = get_session_id()
    session_key = SESSION_DIR + session_id
    info = get_session()

    for k in new_info:
        try:
            del info[k]
        except KeyError:
            pass

    info.id = session_id  # this should not change

    file_storage.setItem(session_key, info)
    return info

def end():
    web.setcookie(COOKIE_NAME, "", expires=0)
    session_id = get_session_id()
    session_key = SESSION_DIR + session_id
    file_storage.delItem(session_key)

# helpers

def get_user_location():
    session_info = session()
    if "lat" in session_info:
        return Storage(lat=session_info.lat, lon=session_info.lon)
    else:
        return None
