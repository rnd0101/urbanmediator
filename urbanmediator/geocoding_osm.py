# -*- coding: utf-8 -*-

# OpenStreetMap geocoder

import urllib, time, datetime, os, sha, sys, re, StringIO

try:
    import elementtree.ElementTree as et
except ImportError:
    # Python >= 2.5.1
    import xml.etree.ElementTree as et

from urbanmediator.util import request_digest

from urbanmediator.geo_support import dist

from urbanmediator.config import file_storage

def loadURL(url):
    CMD = sys.executable + " read_feed.py"
    child_stdin = os.popen(CMD, "w")
    child_stdin.write(url)
    child_stdin.close()

    req_dig = request_digest(url)
    req_dig_key = "CACHE/" + req_dig
    return file_storage.getItem(req_dig_key, mode="file")


addr_re = re.compile("(\d+)")

def street_latlon(address, srs="EPSG:4326", metadata=None):
    metadata = metadata or {}
    address_orig = address
    try:
        address = unicode(address_orig, "utf-8").replace(","," ").replace("_"," ").strip()
    except:
        raise ValueError

    addr = urllib.quote_plus(address.encode("utf-8"))
    url = "http://gazetteer.openstreetmap.org/namefinder/search.xml?find=%s" % addr
    u = urllib.urlopen(url)

    fc = u.read()
    tree = et.parse(StringIO.StringIO(fc))
    root = tree.getroot()

    if " error=" in fc:
        raise ValueError

    if srs.upper() == "EPSG:4326":
        hint_lat = metadata.get("hint_lat", 1.0)
        hint_lon = metadata.get("hint_lon", 1.0)
        best_location = None
        for a in root.findall("named"):
            lat = float(a.attrib.get("lat", 0.0))
            lon = float(a.attrib.get("lon", 0.0))
            zoom = a.attrib.get("zoom", None)
            try:
                description = a.find("description").text
            except:
                description = ""
            if lat or lon:
                md = {'address': address.encode("utf-8"),
                      'description': description,
                        }
                if zoom:
                    md["zoom"] = min(15, int(zoom))
                this_dist = dist((lat, lon), (hint_lat, hint_lon))
                if best_location is None or this_dist < min_dist:
                    best_location = (float(lat), float(lon), md)
                    min_dist = this_dist
        if best_location:
            return best_location
    raise ValueError

supported_srs = ("EPSG:4326",)

# this is to have city-specific examples
def example():
    return "kajavankatu"

def test():
    return street_latlon(example())

if __name__ == "__main__":
    print test()

