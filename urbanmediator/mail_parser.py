# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Parser for the mail message.
"""

import email, sys, re, sha, datetime
from email.Utils import getaddresses
from email.Header import decode_header
import StringIO

import config
import util

from web.utils import Storage

import lmx_parser

BASE_DOMAIN = config.mail_base_domain
SEPARATOR = "[.+:]"
NAME_CHARS = "[a-zA-Z0-9_.=-]"
USER_TO_URL_RE = re.compile(r"(?i)(?P<um>%s+)[.](?P<board_id>\d+)@(?P<domain>%s)" % 
        (NAME_CHARS, BASE_DOMAIN))


def decode_subject(subj):
    return "".join(unicode(s, enc or "utf-8").encode("utf-8") for (s, enc) in decode_header(subj))

def getAttachements(rfcmessage):
    container = []
    message = email.message_from_string(rfcmessage)
    subject = decode_subject(message["subject"])
    
    tos = message.get_all('to', [])
    ccs = message.get_all('cc', [])
    resent_tos = message.get_all('resent-to', [])
    resent_ccs = message.get_all('resent-cc', [])
    all_recipients = getaddresses(tos + ccs + resent_tos + resent_ccs)

    froms = message.get_all('from', [])
    try:
        message_id = message["message-id"]
    except:
        message_id = "not_unique"
    sender = getaddresses(froms)

    recepients = []
    for to_whom_name, to_whom in all_recipients:
        try:
            recepients.append(USER_TO_URL_RE.match(to_whom).groupdict())
        except:
            pass

    counter = 0
    for msg in message.walk():
        if not msg.is_multipart() and msg.get_content_maintype() != 'message':
            ct = msg.get_content_type()
            mtype = msg.get_content_maintype().lower()
            payload = msg.get_payload()
            te = msg.get('Content-Transfer-Encoding', '8bit').lower()
            if te == 'base64':
                try: payload = email.base64MIME.decode(payload)
                except: payload = ''   # ???
            elif te == 'quoted-printable':
                try: payload = email.quopriMIME.decode(payload)
                except: payload = ''   # ???
            if mtype == 'text' or mtype is None:
                try: tc = msg.get_content_charset()
                except: tc = 'latin-1'
            else:
                pass

            if mtype in ('image', 'video', 'audio', 'text', 'application'):
                counter += 1
                name =  dict(msg.get_params() or []).get('name',
                                             'noname-%i.txt' % counter)
            container.append((ct, name, payload))
        else:
            pass
        
    return Storage(sender=sender, 
                   recepients=recepients,
                   subject=subject, 
                   message_id=message_id,
                   container=container,)


def point_from_message(rfcmessage):
    msg = getAttachements(rfcmessage)
    sender = msg.sender[0][1]   #!!!
    point = Storage(_recepients=msg.recepients,
                    author=sender,
                    author_name=msg.sender[0][0],
                    id=msg.message_id,
                    uuid="mail " + msg.message_id,
                    )
    attachments = []
    lmxpoints = []
    for ct, name, payload in msg.container:
        if "nokia.landmark" in ct or "text/xml" in ct:
            try:
                lmxfile = StringIO.StringIO(payload)
                lmxpoints = lmx_parser.parse_lmx(lmxfile)
            except:
                continue
        else:
            attachment = Storage(
                content=payload,
                content_type=ct,
                filename=name,
                author=sender,
            )
            attachments.append(attachment)

    try:
        point.update(lmxpoints[0])
    except:
        point.lat = point.lon = 0.0   # !!! not a point?
    point.attachments = attachments
    point.added = util.now()   #!!!?

    if msg.subject.strip():
        point.title = msg.subject
    # else title comes from landmark's name
    return point

if __name__ == '__main__':
    print point_from_message(open(sys.argv[1]).read())

