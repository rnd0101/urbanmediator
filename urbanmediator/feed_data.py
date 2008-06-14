# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Module for loading and parsing feeds.
    (may need refactorings in the future)
"""

import time, datetime, os, sys, StringIO
try:
    import elementtree.ElementTree as ET
except ImportError:
    # Python >= 2.5.1
    import xml.etree.ElementTree as ET


import feedparser
import media

import config
import util
from util import Entity

import url_handler
from plugins import geocoding, scrapers

def loadFeed(url, aged=None):
    try:
        fc = url_handler.loadURL(url, aged=aged)
        return feedparser.parse(fc)
    except:
        return dict(bozo=True)

def parseGeoTag(gt):
    t1 = "".join([c for c in gt if c in "-.0123456789"])
    #!!! there seems to be no better way:
    if "." not in t1:
        if t1[0] == '-':
            t1 = t1[:3] + "." + t1[3:]
        else:
            t1 = t1[:2] + "." + t1[2:]
    return float(t1)

def parseFeed(url, aged=None):
    feed = loadFeed(url, aged=aged)
    entries = []
    if feed["bozo"]:
        return []


    uuid_prefix = url.split("?")[0] + " "  #
#    uuid_prefix = url + " "  #
#          duplicates automatically fetched points...
#    uuid_prefix = feed.feed["id"]  + " "  
#          has security problems (makes possible to highjack entries)

    for e in feed["entries"]:
        entry = Entity()
        lat = lon = 0
        text = ""
        link = ""

        # pubDate:
        try:
            entry.added = datetime.datetime(*e["updated_parsed"][:7])
        except:
            # lack of date not a show stopper
            entry.added = util.now()  # default

        try:
            entry.title = e["title"].encode("utf-8")
        except:
            # lack of title not a show stopper
            entry.title = '(no title)'

        # URL must be there
        try:
            entry.url = e["link"].encode("utf-8")
        except:
            entry.url = ''

        try:  #!!! ? is it ok or we need to make it differently?
            entry.text = e['summary_detail']['value'].encode("utf-8")
        except KeyError: 
            try:
                entry.text = e['content'][0]['value'].encode("utf-8")
            except:
                entry.text = ''

        tags = []
        for td in e.get("tags", []):
            try:
                if td["scheme"] == 'http://comma-separated.tags.icing.eu':  # !!! special case
                    if td["term"].startswith(u"tags:"):
                        term = td["term"].split(u":", 1)[1]
                    else:
                        term = td["term"]
                    tags.extend(
                     [t.encode("utf-8") for t in term.split(u",")])
                else:
                    tags.extend(
                     [t.encode("utf-8") for t in td["term"].split(u" ")])
            except:
                pass

        entry.tags = " ".join([t.replace(" ", "_") for t in tags])

        lat = lon = 0
        # for lat, lon in tags
        for t in tags:
            if "geo" in t and "lat" in t:
                lat = parseGeoTag(t)
            elif "geo" in t and "lon" in t:
                lon = parseGeoTag(t)

        if e.has_key("gml_pos"):
            lat, lon = map(float, e["gml_pos"].split())
        elif e.has_key("pos"):
            if "," in e["pos"]:
                lat, lon = map(float, e["pos"].split(","))
            else:
                lat, lon = map(float, e["pos"].split())

        if e.has_key("georss_point"):
            lat, lon = map(float, e["georss_point"].split())

        #entry["text"] += str(e.keys())

        # for lat, lon in geoRSS:
        try: lat = float(e["geo_lat"])
        except: pass
        try: lon = float(e["geo_long"])
        except: pass

        entry.lat = lat
        entry.lon = lon

        try:
            entry.author = e["author"].encode("utf-8")
        except:
            entry.author = ''

        try:
            entry.id = e["id"].encode("utf-8")
        except KeyError:
            entry.id = entry["url"] + " " + util.entry_digest(
                dict(entry_added=entry.added,
                    entry_author=entry.author,
                    entry_lat=entry.lat,
                    entry_lon=entry.lon,                                        
                )
            )

        entry.uuid = uuid_prefix + entry["id"]   #!!! assume < 2048 chars

        entry.attachments = []
        if "enclosures" in e:
            for l in e.enclosures:
                try:
                    attachment = Entity(
                        content=None,  # to be fetched if needed
                        content_type=l.type,  #? what if not here?!!!
                        filename=l.href,
                        author=entry.author,    
                    )
                    entry.attachments.append(attachment)
                    entry.text += "\n" + l.href   #!!!
                except:
                    pass

        entries.append(entry)
    return entries



def fetch_enclosure(a):
    if a.content is None:
        a.content = url_handler.loadURL(a.filename)  # really - url
        if a.content:
            try:
                headers = url_handler.getHeaders(a.filename)  # really - url
                a.content_type = dict(headers)["content-type"]
            except:
                a.content_type = "application/octet-stream"

def fetch_feed(urls=None, aged=None):
    aged = aged or config.default_aging 
    urls = urls or []
    all_entries = []
    if not urls:
        return all_entries
    for url in urls:
        if url in scrapers:
            module_name = scrapers[url]
            m = getattr(__import__("scrapers." + module_name), module_name)
            # this helps optimize loads
            url_handler.storeParsedURL(url, "dummy")

            all_entries.extend(m.get_as_feed())
        else:
            all_entries.extend(parseFeed(url, aged=aged))
    return all_entries



GEO = "{http://www.w3.org/2003/01/geo/wgs84_pos#}"
ATOM = "{http://www.w3.org/2005/Atom}"

def parse_entry(xmldata):
    """Parse ATOM entry for ATOM publishing protocol """
    xmlfile = StringIO.StringIO(xmldata)
    
    tree = ET.parse(xmlfile)
    entry = {}

    for el in tree.getroot():
        if el.tag == ATOM + "title":
            entry["title"] = el.text
        elif el.tag == ATOM + "content":
            entry["description"] = el.text
        elif el.tag == ATOM + "updated":
            entry["added"] = el.text
        elif el.tag == ATOM + "category":
            if entry.has_key("tags"):
                entry["tags"] += " " + el.attrib["term"]
            else:
                entry["tags"] = el.attrib["term"]
        elif el.tag == GEO + "lat":
            entry["lat"] = float(el.text)
        elif el.tag == GEO + "long":
            entry["lon"] = float(el.text)
    return entry


# the following code is not used, but may be used in the future

test_query_module = "www.examplesearch.com"

def get_query_results(query="arabianranta", url=test_query_module):
    module_name = url.replace(".", "_")
    if query is None or url not in scrapers:
        return []
    m = __import__("scrapers." + module_name)
    m = getattr(m, module_name)
    try:
        qry_url = m.format_query(query)
        data = url_handler.loadURL(qry_url).read()
    except:
        return []

    return m.parse_results(data)

def test():
    # test is outdated!!!
    test_urls = [
        "http://api.flickr.com/services/feeds/photos_public.gne?tags=vanhakaupunki,geotagged&format=atom",
    ]
    test_urls = [test_url1, test_url2, test_url3, test_url5, test_url10]
    fetch_feed(test_urls)

if __name__ == "__main__":
    print test()
