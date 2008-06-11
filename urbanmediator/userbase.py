# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    This module abstractly handles requests for users.

    Uses internalusers or external identities (via plugins) if needed.
"""

import time

import model
import internalusers
from plugins import identity_services


def _get_identity_service(credentials):
    """Which user is this? (credentials.username is enough) """
    if "@" in credentials.username:
        realm = credentials.username.split("@", 1)[1]
    else:
        realm = None

    if realm is None:
        return internalusers

    identity_service_key = "@" + realm.lower()
    if identity_service_key in identity_services:
        return identity_services[identity_service_key]

    # other possibilities? E.g.
    # return openid.authenticate(credentials)

def authenticate(credentials):
    """ input: credentials
        output: user or None
    """
    # look up identity service
    identity_service = _get_identity_service(credentials)

    # try to authenticate with the identity service
    auth_result = identity_service.authenticate(credentials)
    if not auth_result:
        return None

    # drop password as it is not needed any more    
    credentials.password = auth_result.credentials = auth_result.password =None

    # check if corresponding internal user exists
    iuser = internalusers.check_user(credentials)
    if iuser:
        # if it exists, just give it
        return iuser

    # make internal user corresponding to external one
    group = model.Groups(auth_result.group_name).list()[0]
    user = internalusers.add_user(auth_result, auth_result.profile, 
                                    group=group)

    users = model.Users(username=auth_result.username)
    return users.list()[0]


def check_user(credentials):
    """ does user already exists? """
    return _get_identity_service(credentials).check_user(credentials)

def add_user(credentials, profile, group=None, identity_service=None):
    """ add user """
    if not identity_service:
        return internalusers.add_user(credentials, profile, group)
    # !!!

def change_credentials(user, credentials):
    identity_service = _get_identity_service(user)
    try:
        return internalusers.change_credentials(user, credentials)
    except:
        raise ValueError, "Changing password is not possible"

def modify_user(user, profile):
    # profiles are locally stored !!!
    return internalusers.modify_user(user, profile)

def bad_username(username, identity_service=None):
    if not identity_service:
        return internalusers.bad_username(username)
    #!!!
    return True, "No such identity service"


def bad_password(password, identity_service=None):
    if not identity_service:
        return internalusers.bad_password(password)
    #!!!
    return True, "No such identity service"


#!!! duplicates from internalusers
# No external identities for these two: 
def get_visitor_username():
    # !!! asks for refactoring!
    return "visitor" + str(time.time())[-8:].replace(".", "")

def get_anonymous_username():
    # !!! asks for refactoring!
    return "visitor_" + str(time.time())[-8:].replace(".", "")

def get_feed_username(feeduser):
    return "*" + feeduser

