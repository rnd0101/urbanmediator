# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    User management for Icing users.
"""

import re, time

from util import Entity

try:
    from plugins import iisys2
except:
    pass


def authenticate(credentials):
    prepared_credentials = Entity(credentials)
    prepared_credentials.username, realm = credentials.username.split("@", 1)

    vi = iisys2.identity_verification
    result = vi.verify_identity(prepared_credentials, {'realm': realm})
    if result == "success":
        return Entity(
            credentials=None,
            username=credentials.username,
            password=None,
            profile=Entity(),
            group_name="users",
        )
