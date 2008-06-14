# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Triggers
"""


import datetime

import config
import util

def sendmail_adapter(project, trigger, **params):
    if trigger.trigger_action == "test":
        pass # !!!
    elif trigger.trigger_action in ("send", "sendmail"):
        if trigger.url.lower().startswith("mailto:"):
            mailaddr = trigger.url[len("mailto:"):]
            pass

def test_adapter(project, trigger, **params):
    if trigger.trigger_action == "test":
        print "TRIGGER TEST"
        print project, params

def fire_trigger(project, trigger, **params):
    try:
        if trigger.adapter == "test":
            test_adapter(project, trigger, **params)
        elif trigger.adapter in ("sendmail", "mailsender"):
            sendmail_adapter(project, trigger, **params)
        return
    except:
        pass

