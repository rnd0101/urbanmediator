# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Geodetical functions
"""

from math import sin, cos, asin, sqrt, pi, log
import re

def degToRad(x):
    return x*pi/180.0

GA_RE = re.compile("^([0-9]{1,3})([0-9][0-9][.][0-9]+)$")

def gaToDeg(ga_value, ga_letter):
    """
    ga_value is latitude ot longitude in the form: [D]DDMM.SSss
    where D - degrees, MM - minutes, SSss seconds and 100th of seconds
    ga_letter is N, S, W, E (we need it for correct sign)
    """
    m = GA_RE.match(ga_value)
    D, M = m.groups()
    
    return float(D) + float(M) / 60.

def dist((lat1, lon1), (lat2, lon2)):
    """ 
    Input: in degrees, output in meters
    Haversine Formula 
     (from R.W. Sinnott, "Virtues of the Haversine", Sky and Telescope, vol. 68, no. 2, 1984, p. 159)
    for distances between two points
    """
    R = (6378. - 21. * sin(lat1))*1000  # Earth radius for the latitude
    lat1, lon1, lat2, lon2 = map(degToRad, (lat1, lon1, lat2, lon2))
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat*0.5)**2 + cos(lat1) * cos(lat2) * sin(dlon*0.5)**2
    d = 2 * R * asin(min(1,sqrt(a)))
    return d

def meters_per_deg(lat, lon):
    """ how many meters in one lat/lon degree?
    The result can be used for calculating estimates for small
    distances between points
    """
    x = dist((lat, lon), (lat, lon+0.01)) / 0.01   #meters/degree
    y = dist((lat, lon), (lat+0.01, lon)) / 0.01   #meters/degree
    return x, y

#!!! the following function is very wrong
def zoom_from_dist(d):
    """Guess OL zoom level based on the distance """
    return max(8, min(20, int(20 - log(d))))


try:
    from pyproj import Proj, transform

    #wgs84 = Proj(proj='latlong', datum='WGS84')
    wgs84 = Proj(init='epsg:4326')

    def coord_encode(x, y, srsname):
        """ lon, lat """
        srs = Proj(init=srsname.lower());
        x1, y1, z1 = transform(wgs84, srs, y, x, 0.0)
        return y1, x1

    def coord_decode(x, y, srsname):
        """ """
        srs = Proj(init=srsname.lower());
        x1, y1, z1 = transform(srs, wgs84, y, x, 0.0)
        return y1, x1

    coord_conversions = True
except:
    coord_conversions = None
