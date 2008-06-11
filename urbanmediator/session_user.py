# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Handles user sessions. Build upon UM's session module.
    N.B. External users can't authenticate via WSSE.
"""

import web

import model, session as session_manager
import internalusers

def get_user():
    if "current_user" in web.ctx:
        return web.ctx.current_user
    session = session_manager.session()
    if "user_id" in session and session.user_id:
        users = model.Users(id=session.user_id)
        users.annotate_by_groups()
        try:
            web.ctx.current_user = user = users.list()[0]
            return user
        except:
            pass
        del users

def get_wsse_user():
    if "current_user" in web.ctx:
        return web.ctx.current_user
    wsse = web.ctx.env.get('HTTP_X_WSSE', '')
    if not wsse:
        return None
    credentials = model.Storage(wsse=wsse)
    user = internalusers.authenticate(credentials)
    if user:
        web.ctx.current_user = user
        return user
    return None

def bind_user(user):
    session_manager.update_info({'user_id': user.id})

def unbind_user():
    session_manager.remove_info({'user_id': None})
    web.ctx.current_user = None

