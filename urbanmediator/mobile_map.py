# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Module to produce maps for mobile.
    Simple static will do
    (needs refactorings)

    Several classes are for cases when there are two
    coordinate systems used.
    
    Internally, WGS84 is used. Representational SRS
    may be different.

    OSM uses fixed resolutions.

    This module needs refactoring!

"""

import urllib, StringIO, math, os

import PIL.Image as Image

import web
from web.utils import Storage

import config
import url_handler

import geo_support

import model

# ratio used for zoom. Heuristically found
ZOOM_LAT = 2.5
ZOOM_LON = 2.5

#!!!
SAFE_IN_REQUEST = ":,/"
SAFE_IN_REQUEST = ""

def _urlenc(query):
    return "&".join([urllib.quote(str(k), safe=SAFE_IN_REQUEST) + "=" +
                     urllib.quote(str(v), safe=SAFE_IN_REQUEST)
                        for k, v in query.items()])

def wms_url(**context):
    # center not used yet.
    map_base_url = context["getmap_server"]
    data = dict(
        REQUEST="GetMap",
        SERVICE="WMS",
        VERSION="1.1.1",
        LAYERS=context["layers"],
        STYLES="",
        FORMAT="image/jpeg",
        BGCOLOR="0xFFFFFF",
        TRANSPARENT="TRUE",
        SRS=context["srsname"],
        BBOX=",".join(map(str, context["bbox"])),
        WIDTH=context["width"],
        HEIGHT=context["height"],
    )
    return context["getmap_server"] + _urlenc(data)

def draw_points(from_file, coords, marker, pixbox, draft=False):
    """Draw upon map"""
    im = Image.open(from_file)
    if im.mode != 'RGB' and im.mode != 'CMYK': 
        im = im.convert('RGB')
    if draft:
        im.draft("L", pixbox)
    marker = Image.open(open(marker, "r"))
    markerw, markerh = marker.getbbox()[2:]
    dx, dy = markerw / 2, markerh / 2

    for x, y in coords:
        # Trick: using Alfa-layer as mask
        try:
            im.paste(marker, (int(x-dx), int(y-dy)), marker)
        except:
            im.paste(marker, (int(x-dx), int(y-dy)))

    out_file = StringIO.StringIO()
    im.save(out_file, format='JPEG')
    return out_file.getvalue()

def get_bbox(lat, lon, zoom):
    # Zoom level handling should be refactored !!! XXX
    k1 = zoom*ZOOM_LON
    k2 = zoom*ZOOM_LAT
    return (lon-k1, lat-k2, lon+k1, lat+k2)

def calc_params(top, left, width, height, z):
    extent_left = -20037508
    extent_top = 20037508.34

    res = get_osm_resolution(z)

    x = int(math.floor((left - extent_left) / (res * width))) 
    y = int(math.floor((extent_top - top) / (res * height)))

    x1 = (left - extent_left) / (res * width)
    y1 = (extent_top - top) / (res * height)

    dx = (x1 - x) * width
    dy = (y1 - y) * height
    limit = 2 ** z
    x = ((x % limit) + limit) % limit
    return x, y, dx, dy

def osm_url(lat, lon, width, height, getmap_server, z=14):
    import sys
    x, y, dx, dy = calc_params(lat, lon, width, height, z)
    return config.getmap_custom_server + "%s/%s/%s" % (z, x, y) + "." + "png", dx, dy

def serve_osm_map(point, points=None, zoom=14, mapx=300, mapy=300, marker=None, draft=False):
    """Print map given central point lat, lon and zoom (and some other parameters)"""
    # Zoom level handling should be refactored !!! XXX
    marker = marker or config.static_dir + "/img/marker.png"
    points = points or []
    lat, lon = model.geo_encode(float(point.lat), float(point.lon))  #!!!
    pixbox = (256, 256)

    url, dx, dy = osm_url(
            lat=lat,
            lon=lon,
            width=pixbox[0],    #!!!
            height=pixbox[1],
            getmap_server=config.getmap_custom_server,
            z=zoom,   #!!!
    )

    try:
        headers, fh = url_handler.loadURL2(url, 
            cache_dir="MAP_CACHE/", aged=1000000)
    except KeyError:
        headers = {"content-type": "image/jpeg"}
        fh = open(config.static_dir + "/broken_map.jpg")
        # WMS not available???

    # trying to find y, x from lat, lon
    pixcoords = [(dx, dy)]
    
    print draw_points(fh, pixcoords, marker, pixbox, draft=draft) #!!!
    

    try:
        web.header("content-type", headers["content-type"])
    except:
        pass

def get_osm_resolution(zoom):
    max_res = 156543.0339;
    return max_res / 2**zoom

def get_osm_resolutions():
    max_res = 156543.0339;
    return [max_res / 2**zoom for zoom in range(0, 18)]

def click_coord_hybrid_osm(x, y, c_lat, c_lon, zoom=0, mapx=300, mapy=300):
    res = get_osm_resolution(zoom)
    lat, lon = model.geo_encode(float(c_lat), float(c_lon))
    cx, cy, dx, dy = calc_params(lat, lon, mapx, mapy, zoom)
    lat1 = lat - res * (y - dy)
    lon1 = lon + res * (x - dx)
    return model.geo_decode(lat1, lon1)

def serve_map(point, points=None, zoom=0.001, mapx=300, mapy=300, marker=None, draft=False):
    """Print map given central point lat, lon and zoom (and some other parameters)"""
    # Zoom level handling should be refactored !!! XXX
    marker = marker or config.static_dir + "/img/marker.png"
    points = points or []
    lat, lon = float(point.lat), float(point.lon)
    bbox = get_bbox(lat, lon, zoom)
    pixbox = (mapx, mapy)

    if zoom < 0.003:
        getmap_layers = config.getmap_layers
    else:
        getmap_layers = config.getmap_layers1

    url = wms_url(
            bbox=model.encode_bbox(*bbox),  #!!!
            layers=getmap_layers,
            width=pixbox[0],    #!!!
            height=pixbox[1],
            getmap_server=config.getmap_server,
            srsname=config.srsname,
            )

    try:
        headers, fh = url_handler.loadURL2(url, 
            cache_dir="MAP_CACHE/", aged=1000000)
    except KeyError:
        headers = {"content-type": "image/jpeg"}
        fh = open(config.static_dir + "/broken_map.jpg")
        # WMS not available???
        

    # trying to find y, x from lat, lon
    pixcoords = []
    for p in points + [point]:
        ly = float(p.lat)
        lx = float(p.lon)

        px = (lx - bbox[0]) * pixbox[0] / (bbox[2]-bbox[0])
        py = (ly - bbox[1]) * pixbox[1] / (bbox[3]-bbox[1])
        if 11 < px < pixbox[0] and 11 < py < pixbox[1]:
            pixcoords.append((px, pixbox[1] - py))
        
    print draw_points(fh, pixcoords, marker, pixbox, draft=draft) #!!!
    try:
        web.header("content-type", headers["content-type"])
    except:
        pass


def click_coord(x, y, c_lat, c_lon, zoom=0.001, mapx=300, mapy=300):
    bbox = get_bbox(c_lat, c_lon, zoom)
    pixbox = (mapx, mapy)
    lon = (bbox[2] - bbox[0]) * x / pixbox[0] + bbox[0]
    lat = (bbox[3] - bbox[1]) * (pixbox[1] - y) / pixbox[1] + bbox[1]
    return lat, lon

class MapContext(Storage):
    def step(self):
        return get_resolution(self.zoom) * self.get("step", 100)

    def up(self, step=100):
        return self.links("map", 
            **MapContext(lat=self.lat+self.zoom*ZOOM_LAT*.7, lon=self.lon, zoom=self.zoom))

    def down(self, step=100):
        return self.links("map", 
            **MapContext(lat=self.lat-self.zoom*ZOOM_LAT*.7, lon=self.lon, zoom=self.zoom))

    def left(self, step=100):
        return self.links("map", 
            **MapContext(lat=self.lat, lon=self.lon-self.zoom*ZOOM_LON*.7, zoom=self.zoom))

    def right(self, step=100):
        return self.links("map", 
            **MapContext(lat=self.lat, lon=self.lon+self.zoom*ZOOM_LON*.7, zoom=self.zoom))

    def zoomin(self):
        return self.links("map", 
            **MapContext(lat=self.lat, lon=self.lon, zoom=self.zoom*0.66))

    def zoomout(self):
        return self.links("map", 
            **MapContext(lat=self.lat, lon=self.lon, zoom=self.zoom/0.66))



def get_resolution(zoom):
    resolutions = [float(r) for r in 
        config.getmap_resolutions.replace("[", "").replace("]", "").replace(" ", "").split(",")]
    try:
        return zoom, resolutions[zoom]
    except:
        return 0, resolutions[0]
    

def get_bbox_repr(lat, lon, resolution, pixbox):
    (mapx, mapy) = pixbox
    k1 = resolution * mapx / 2.0
    k2 = resolution * mapy / 2.0
    return (lon-k2, lat-k1, lon+k2, lat+k1)

def calculate_deltas(bbox, point):
    try:
        corner_point = model.Point(repr_lat=bbox[3], repr_lon=bbox[2])
        model.decode_coordinates(corner_point)
        model.decode_coordinates(point)
        return corner_point.lat - point.lat, corner_point.lon - point.lon
    except:
        return 0.01, 0.01


def serve_map_repr(point, points=None, zoom=1, mapx=300, mapy=300, marker=None, draft=False):
    """Print map given central point repr_lat, repr_lon and zoom (and some other parameters)"""

    marker = marker or config.static_dir + "/img/marker.png"
    zoom, resolution = get_resolution(zoom)

    points = points or []
    lat, lon = float(point.repr_lat), float(point.repr_lon)
    pixbox = (mapx, mapy)
    bbox = get_bbox_repr(lat, lon, resolution, pixbox)

    # same as in JavaScript
    if zoom > config.getmap_zoom2 + config.getmap_zoomshift:
        if zoom > config.getmap_zoom1 + config.getmap_zoomshift:
            getmap_layers = config.getmap_layers
        else:
            getmap_layers = config.getmap_layers1
    else:
         getmap_layers = config.getmap_layers2

    url = wms_url(
            bbox=bbox,
            layers=getmap_layers,
            width=pixbox[0],    #!!!
            height=pixbox[1],
            getmap_server=config.getmap_server,
            srsname=config.srsname,
            )

    try:
        headers, fh = url_handler.loadURL2(url, 
            cache_dir="MAP_CACHE/", aged=1000000)
    except KeyError:
        headers = {"content-type": "image/jpeg"}
        fh = open(config.static_dir + "/broken_map.jpg")
        # WMS not available???
        
    if marker is not None:
        # trying to find y, x from lat, lon
        pixcoords = []
        for p in points + [point]:
            ly = float(p.repr_lat)
            lx = float(p.repr_lon)

            px = (lx - bbox[0]) * pixbox[0] / (bbox[2]-bbox[0])
            py = (ly - bbox[1]) * pixbox[1] / (bbox[3]-bbox[1])
            if 11 < px < pixbox[0] and 11 < py < pixbox[1]:
                pixcoords.append((px, pixbox[1] - py))
        
        print draw_points(fh, pixcoords, marker, pixbox, draft=draft) #!!!
    else:
        print fh.read()

    web.header("delta", "%s %s" % calculate_deltas(bbox, point))

    try:
        web.header("content-type", headers["content-type"])
    except:
        pass

def click_coord_repr(x, y, c_lat, c_lon, zoom=1, mapx=300, mapy=300):
    bbox = get_bbox_repr(c_lat, c_lon, zoom)
    pixbox = (mapx, mapy)
    lon = (bbox[2] - bbox[0]) * x / pixbox[0] + bbox[0]
    lat = (bbox[3] - bbox[1]) * (pixbox[1] - y) / pixbox[1] + bbox[1]
    return lat, lon


def get_resolutions_array():
    return [float(r) for r in 
        config.getmap_resolutions.replace("[", "").replace("]", "").replace(" ", "").split(",")]


def get_corrected_zoom(zoom, resolutions):
    if not (0 <= zoom < len(resolutions)):
        return min(max(int(zoom), 0), len(resolutions)-1)
    else:
        return int(zoom)

def get_resolution_hybrid(lat, lon, zoom, resolutions):
    m_per_deg = geo_support.meters_per_deg(lat, lon)
    if config.srsname.lower() == "epsg:4326":
        # quick unscientific fix
        return resolutions[zoom] * 0.8, resolutions[zoom] / m_per_deg[0] * m_per_deg[1] * 0.8
    else:
        return resolutions[zoom] / m_per_deg[1], resolutions[zoom] / m_per_deg[0]

def get_bbox_hybrid(lat, lon, resolution, pixbox):
    (mapx, mapy) = pixbox
    k1 = resolution[0] * mapx / 2.0
    k2 = resolution[1] * mapy / 2.0
    return (lon-k2, lat-k1, lon+k2, lat+k1)

def click_coord_hybrid(x, y, c_lat, c_lon, zoom=0, mapx=300, mapy=300):
    resolutions = get_resolutions_array()
    zoom = get_corrected_zoom(zoom, resolutions)
    resolution = get_resolution_hybrid(c_lat, c_lon, zoom, resolutions)
    lat = c_lat - resolution[0] * (y - mapy / 2.0)
    lon = c_lon + resolution[1] * (x - mapx / 2.0)
    
    return lat, lon

class MapContextHybrid(Storage):
    """ Calculations for new coordinates and zoom level
        for panning and zooming.
    """
    def res(self):
        resolutions = get_resolutions_array()
        self.zoom = get_corrected_zoom(self.zoom, resolutions)
        res_hybrid = get_resolution_hybrid(self.lat, self.lon, self.zoom, resolutions)
        return res_hybrid

    def max_zoom(self):
        return config.getmap_resolutions.count(",") + 1

    def step_lat(self):
        return self.res()[0] * self.get("step", self.step)

    def step_lon(self):
        return self.res()[1] * self.get("step", self.step)

    def up(self, step=100):
        self.step = step
        return self.links("map", 
            lat=self.lat+self.step_lat(), lon=self.lon, zoom=self.zoom)

    def down(self, step=100):
        self.step = step
        return self.links("map", 
            lat=self.lat-self.step_lat(), lon=self.lon, zoom=self.zoom)

    def left(self, step=100):
        self.step = step
        return self.links("map", 
            lat=self.lat, lon=self.lon-self.step_lon(), zoom=self.zoom)

    def right(self, step=100):
        self.step = step
        return self.links("map", 
            lat=self.lat, lon=self.lon+self.step_lon(), zoom=self.zoom)

    def zoomin(self, step=1):
        if self.zoom + step >= self.max_zoom():
            return self.links("map", 
                lat=self.lat, lon=self.lon, zoom=self.zoom)
        return self.links("map", 
            lat=self.lat, lon=self.lon, zoom=self.zoom+step)

    def zoomout(self, step=1):
        if self.zoom - step < 0:
            return self.links("map",
                lat=self.lat, lon=self.lon, zoom=self.zoom)
        return self.links("map", 
            lat=self.lat, lon=self.lon, zoom=self.zoom-step)


class MapContextHybridOSM(MapContextHybrid):
    def res(self):
        resolutions = get_osm_resolutions()
        self.zoom = get_corrected_zoom(self.zoom, resolutions)
        res_hybrid = get_resolution_hybrid(self.lat, self.lon, self.zoom, resolutions)
        return res_hybrid

    def max_zoom(self):
        return len(get_osm_resolutions())

    def step_lat(self):
        return self.res()[0] * self.get("step", self.step) * .5

    def step_lon(self):
        return self.res()[1] * self.get("step", self.step) * .5


if __name__ == "__main__":
    # !!! old test
    ll = click_coord(150, 150, 60.1708996667, 24.93546, 
            zoom=0.001, mapx=300, mapy=300)
    print ll



