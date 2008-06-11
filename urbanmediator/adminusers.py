# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    User management for internal admin users.

    However, interface sets example for any external identities
"""

import re, time

from util import Entity

def authenticate(credentials):
    from config import admin_credentials
    for c in admin_credentials:
        if credentials.username.lower() == c["username"] and \
           credentials.password == c["password"]:
            # possibly other things
            return Entity(
                credentials=None,
                username=c["username"],
                password=None,
                profile=Entity(),
                group_name="administrators",
            )
