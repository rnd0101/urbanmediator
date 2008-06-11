# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Parser for the Nokia's(tm) LMX format for POI exchange.

"""

try:
    import elementtree.ElementTree as et
except ImportError:
    # Python >= 2.5.1
    import xml.etree.ElementTree as et

LM = "{http://www.nokia.com/schemas/location/landmarks/1/0}"

def el(el, path, default=None):
    findpath = LM + ("/" + LM).join(path.split("/"))
    try:
        return el.find(findpath).text
    except:
        return default

def els(el, path):
    findpath = LM + ("/" + LM).join(path.split("/"))
    try:
        return [e.text for e in el.findall(findpath)]
    except:
        return []


def parse_lmx(inpfile):
    tree = et.parse(inpfile)
    points = []
    for landmark in tree.findall("//" + LM + "landmark"):
        point = {}
        point["lat"] = float(el(landmark, "coordinates/latitude", 0.0))
        point["lon"] = float(el(landmark, "coordinates/longitude", 0.0))

        point["title"] = el(landmark, "name", "")
        point["text"] = el(landmark, "description", "")

        point["country"] = el(landmark, "addressInfo/country", "")
        point["city"] = el(landmark, "addressInfo/city", "")
        point["street"] = el(landmark, "addressInfo/street", "")

        # all tags
        point["tags"] = els(landmark, "category/name")

        # only first one...
        point["url"] = el(landmark, "mediaLink/url")

        points.append(point)
    return points

if __name__ == "__main__":
    print parse_lmx(file("d.lmx"))
    print parse_lmx(file("k.lmx"))
