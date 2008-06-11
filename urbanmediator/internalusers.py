# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.
    
    User management for internal users.

    Interface sets example for any external identities
"""

import re, time

import model
import database


GOOD_USERNAME_RE = re.compile("^[a-zA-Z0-9 ._-]{2,32}$")
GOOD_USERNAME_RE = re.compile("^[a-zA-Z0-9 ._-]+$")
RESERVED_USERNAME_RE = re.compile("^(visitor|guest|admin|external|anonymous).+$")

def bad_username(username):
    """If username is bad, return nonempty string"""
    if GOOD_USERNAME_RE.match(username):
        if RESERVED_USERNAME_RE.match(username):
            return True, "User name is reserved or forbidden"
        return False, ""
    return True, "Bad user name"

def bad_password(password):
    """If password is bad, return nonempty string"""
    if len(password) < 2:
        return True, "Too short"
    return False, ""

def authenticate(credentials):
    """ input: credentials
        output: user or None
    """
    users = model.Users(credentials=credentials)
    if not users:
        return None
    return users.list()[0]  # ???

def add_user(credentials, profile, group=None):
    """
        output: user (if created) or None (on failure)
    """
    if check_user(credentials):
        return None      # user already exists

    user = model.User(credentials)
    model.Users.store(user, profile, group)

    return check_user(credentials)  # now should be successful

def check_user(credentials):
    try:
        users = model.Users(username=credentials.username)
        if users:   #!!! and users.list()[0].credentials != None:
            return users.list()[0]  # user already exists
        else:
            return None
    except:
        del users   # do not leak user passwords!
        return None

def change_credentials(user, credentials):
    user.password = credentials.password
    model.Users.store(user, profile=None, group=None)

def modify_user(user, profile):
    user.password = None  # no change
    model.Users.store(user, profile, group=None)

def delete_user(user):
    pass

def add_group(group):
    pass

def delete_group(group):
    pass

def get_group(group):
    pass

def get_visitor_username():
    # !!! asks for refactoring!
    return "visitor" + str(time.time())[-8:].replace(".", "")

def get_anonymous_username():
    # !!! asks for refactoring!
    return "anonymous" + str(time.time())[-8:].replace(".", "")

def get_feed_username(feeduser):
    return "*" + feeduser
