#!/usr/bin/python

"""
Read an email from stdin and forward it to a url
 
Usage: mail_to_http.py url
where
       url - to POST email
 
(Inspired by  smtp2zope.py)
"""

import sys, urllib

if len(sys.argv) == 1:
    print __doc__
    sys.exit(1)
        
url   = sys.argv[1]

urllib.urlopen(url, data=urllib.urlencode({'Mail': sys.stdin.read()}))

sys.exit(0)
