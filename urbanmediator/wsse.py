# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    This module provides WSSE checking for client and server.

    Function to be used from this module are:
        auth_request(username, password)

        auth_reply(wsse, pwdfunc)

        where pwdfunc(username) -> password
        is given. And wsse is the string value of the X-WSSE field.

        Works for Pys60 as well as for the Python 2.2 and up.
"""

import base64, time, random, re
try:
    import sha as sha1
except ImportError:
    import shaone as sha1

def gen_nonce():
    return "".join([hex(random.randrange(0x1000, 0x100000))[2:] for x in range(5)])

def _pwd_digest(nonce, created, password):
    return base64.encodestring(sha1.new(nonce + created + password).digest()).replace("\n", "")

def auth_request(username, password):
    """client side generation of request"""
    created = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time()))
    nonce = gen_nonce()
    passdigest = _pwd_digest(nonce, created, password)
    return {
        'Authorization': 'WSSE profile="UsernameToken"',
        'X-WSSE': 'UsernameToken Username="%s", PasswordDigest="%s", Nonce="%s", Created="%s"' % (username, passdigest, nonce, created)
    }

XWSSE_RE = re.compile('''([A-Za-z]+)\s*=\s*["'](.*?)["']''')   #"

def _parse_wsse(wsse):
    wssed = {}
    for m in XWSSE_RE.findall(wsse):
        wssed[m[0].lower()] = m[1]
    return wssed["username"], wssed["passworddigest"], wssed["nonce"], wssed["created"]


def auth_reply(wsse, pwdfunc):
    """server-side auth check. XXX !!! needs to check date"""
    try:
        username, passdigest, nonce, created = _parse_wsse(wsse)
        password = pwdfunc(username)
        passdigest1 = _pwd_digest(nonce, created, password)
    except StandardError:
        return None
    del password, nonce
    if passdigest == passdigest1:
        return username
    else:
        return None
    

def test_pwdfunc(username):
    pwd = {'bob': 'werwer'}
    return pwd[username]

def test():
    req = auth_request("bob", "werwer")
    rep = auth_reply(req["X-WSSE"], test_pwdfunc)
    print req, rep

def test1(s):
    print _parse_wsse(s)

if __name__ == "__main__":
    test()
    test1('''UsernameToken Username="bob", PasswordDigest="zRdWRKFm9Zi7QbrDizkth5XQnt4=", Nonce="59def499dc3a2c1d48133d279", Created="2008-04-09T12:49:46Z"''')

