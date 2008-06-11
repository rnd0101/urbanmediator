# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Triggers for access to Icing webservices.
"""


import datetime

import config
import util

try:
    from plugins import ismart
except:
    pass

try:
    from plugins import iisys
except:
    pass

# XXX

def ismart_adapter(project, trigger, **params):
    point = params["point"]
    if trigger.trigger_action == "delete":
        if "dac" in point.uuid.lower():
            dac = point.uuid.split()[1]
            di = ismart.delete_issue
            res = di.delete_issue(dac)
            mb = open("TESTISMART", "a")
            mb.write(str(trigger) + "\n" + str(params) + "\n" + res)
            mb.close()
        return
    ir = ismart.issue_reporter    #!!! 
    # if trigger.trigger_action == "insert":
    images = ""
    attachment = params.get("attachment", {})
    if attachment:
        images = ir.issue_images([attachment])
    res = ir.create_issue(
            issue_id=trigger.url + "%s" % point.id,
            app_user_id="notyet",
            user_name=params["user"].username,  # "usernametobe",
            user_email="",
            issue_datetime=ir.xsd_datetime(util.now()),  #!!!
            subject=params["point"].title,
            description=util.first_line(point.description, length=32000),  #!!!?
            language="en",
            images=images,
            freeclassifiers=ir.freeclassifiers(
              [ir.iisys_data.Entity(
                    term=t.safetag, schema="http://icing.arki.uiah.fi/",
                    ) for t in point.tags]),   #!!!
            weblinks=ir.weblinks([ir.iisys_data.Entity(
                                link=point.url, title="link",
                                ),
                                ]),   #!!!
            lat=str(point.lat),
            lon=str(point.lon),
    )
    mb = open("TESTISMART", "a")
    mb.write(str(trigger) + "\n" + str(params) + "\n" + res)
    mb.close()


def iisys_adapter(project, trigger, **params):
    ir = iisys.issue_reporter   #!!!
    point = params["point"]
    images = ""
    attachment = params.get("attachment", {})
    if attachment:
        images = ir.issue_images([attachment])
    res = ir.create_issue(
            issue_id=trigger.url + "%s" % point.id,
            app_user_id="notyet",
            user_name=params["user"].username,  # "usernametobe",
            user_email="",
            issue_datetime=ir.xsd_datetime(util.now()),  #!!!
            subject=params["point"].title,
            description=util.first_line(point.description, length=32000) + " .",  #!!!?
            language="en",
            images=images,
            freeclassifiers=ir.freeclassifiers(
              [ir.iisys_data.Entity(
                    term=t.safetag, schema="http://icing.arki.uiah.fi/",
                    ) for t in point.tags]),   #!!!
            weblinks=ir.weblinks([ir.iisys_data.Entity(
                                link=point.url, title="link",
                                ),
                                ]),   #!!!
            lat=str(point.lat),
            lon=str(point.lon),
    )
    mb = open("TESTIISYS", "a")
    mb.write(str(trigger) + "\n" + str(params["point"]) + "\n" + res)
    mb.close()



def sendmail_adapter(project, trigger, **params):
    if trigger.trigger_action == "test":
        print "TESTING SENDMAIL"
        print "_+_+_+_+_+_+_+_+"
    elif trigger.trigger_action in ("send", "sendmail"):
        if trigger.url.lower().startswith("mailto:"):
            mailaddr = trigger.url[len("mailto:"):]
            mb = open("TESTMAILBOX", "a")
            mb.write(str(trigger) + "\n" + str(params))
            mb.close()

# XXX


def test_adapter(project, trigger, **params):
    if trigger.trigger_action == "test":
        print "TRIGGER TEST"
        print project, params

def fire_trigger(project, trigger, **params):
    try:
        if trigger.adapter == "test":
            test_adapter(project, trigger, **params)
        elif trigger.adapter == "ismart":
            ismart_adapter(project, trigger, **params)
        elif trigger.adapter == "iisys":
            iisys_adapter(project, trigger, **params)
        elif trigger.adapter in ("sendmail", "mailsender"):
            sendmail_adapter(project, trigger, **params)
        return
    except:
        pass

