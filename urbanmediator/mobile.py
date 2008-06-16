# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Mobile web UI controller.
"""

import web
from web.utils import Storage

import model
import media
import util
import i18n
import config
import turing
import url_handler
import mobile_map
import acl
import userbase
import view
import session
from profiles import *
from session_user import *
from view import mobile_macro as macros, mobile_render as render, \
                mobile_get_page as get_page
from links import pc_links, feed_links, mobile_links as links

_ = i18n._

MOBILE_SCRIPTS = 'loc.py', 'default.py'

urls = (
    '/point_list.html', 'PointList',
    '/point.html', 'Point',
    '/add_point.html', 'AddPoint',
    '/place.html', 'MobileMap',
    '/search.html', 'Search',
    '/info.html', 'Info',
    '/login', 'Login',
    '/logout', 'Logout',
    '/', 'Index',
    '/map(?:.html)?', 'MobileMap',    # should be under this url (mobile script expects it!)
    '/map_action.html/([0-9.-]+),([0-9.-]+),([0-9.-]+),([0-9.-]+),([0-9.-]+)', 'MapAction',
    '/m/(%s)' % "|".join(MOBILE_SCRIPTS), 'MobileScript',
    '/locationmap', 'LocationMap',               # !!! these
    '/locationmapclean', 'LocationMapClean',     # !!! needs to be refactored
    '/locationmaprepr', 'LocationMapRepr',       # !!!
)

base_url = config.base_url
mobile_base_url = config.base_url + '/mobile/'

web.template.Template.globals.update(dict(
    mobile_links=links,
))


def autologin(i):
    if i.get("username", None) and i.get("password", None):
        credentials = Storage(username=i.username,
                              password=i.password)

        user = userbase.authenticate(credentials)
        if user:
            bind_user(user)
            return user, "logged in"
    return None, "no login or invalid login"


class MobileScript:

    def GET(self, script_name):
        script = open(config.static_dir + "/m/" + script_name.replace("..", "") + "t").read()
        script = script.replace("@mobile_base_url@", mobile_base_url.rstrip("/"))
        script = script.replace("@debug_fmt@", "/mobile/map?debug=%(debug)s&username=%(username)s&password=%(password)s")
        script = script.replace("@latlon_fmt@", "/mobile/map?gps=ok&lat=%(lat)s&lon=%(lon)s&debug=%(debug)s&username=%(username)s&password=%(password)s")
        script = script.replace("@number_of_tries@", "5")
        script = script.replace("@number_of_tries_gps@", "3")
        print script


class LocationMap:
    def GET(self):
        i = web.input(lat=None, lon=None, zoom=None, mapx=300, mapy=300, draft="0")
        if i.lat and i.lon:
            point = Storage(lat=float(i.lat), lon=float(i.lon))
            model.encode_coordinates(point)
        i.zoom = float(i.zoom or (config.mobile_zoom + config.getmap_zoomshift))
        if config.getmap_custom_wms == "wms":
            mobile_map.serve_map(point, zoom=i.zoom, mapx=int(i.mapx), mapy=int(i.mapy),
        #    marker='static/pc_files/img/icons/point_medium.png'
            draft=int(i.draft),
            )
        else:
        # osm
            mobile_map.serve_osm_map(point, zoom=int(i.zoom), mapx=int(i.mapx), mapy=int(i.mapy),
        #    marker='static/pc_files/img/icons/point_medium.png'
            draft=int(i.draft),
            )


class LocationMapClean:
    def GET(self):
        i = web.input(lat=None, lon=None, zoom=None, mapx=200, mapy=200, draft="0", marker="1")
        if i.lat and i.lon:
            point = Storage(lat=float(i.lat), lon=float(i.lon))
            model.encode_coordinates(point)
        i.zoom = float(i.zoom or (config.mobile_zoom + config.getmap_zoomshift))
        if config.getmap_custom_wms == "wms":
            mobile_map.serve_map_repr(point, zoom=int(i.zoom), mapx=int(i.mapx), mapy=int(i.mapy),
                marker=(i.marker == "1") and config.static_dir + '/img/cross-hair.png' or None,
                draft=int(i.draft),
            )
        else:
            mobile_map.serve_osm_map(point, zoom=int(i.zoom), mapx=int(i.mapx), mapy=int(i.mapy),
                marker=(i.marker == "1") and config.static_dir + '/img/cross-hair.png' or None,
                draft=int(i.draft),
            )


class LocationMapRepr:
    def GET(self):
        i = web.input(repr_lat=None, repr_lon=None, zoom=None, mapx=300, mapy=300, draft="0")
        if i.repr_lat and i.repr_lon:
            point = Storage(repr_lat=float(i.repr_lat), repr_lon=float(i.repr_lon))
            model.decode_coordinates(point)
        i.zoom = float(i.zoom or (config.mobile_zoom + config.getmap_zoomshift))
        if config.getmap_custom_wms == "wms":
            mobile_map.serve_map_repr(point, zoom=int(i.zoom), mapx=int(i.mapx), mapy=int(i.mapy),
            #    marker='static/pc_files/img/icons/point_medium.png'
                draft=int(i.draft),
            )
        else:
            mobile_map.serve_osm_map(point, zoom=int(i.zoom), mapx=int(i.mapx), mapy=int(i.mapy),
                marker=config.static_dir + '/img/cross-hair.png',
                draft=int(i.draft),
            )



def nav_data(**links):
    return [
    #    Storage(key='add', label=_('label_Add'), link=links['add']),
        Storage(key='loc', label=_('label_Place'), link=links['loc']),
    #    Storage(key='hom', label=_('label_Home'), link=links['hom']),
        Storage(key='sea', label=_('label_Search'), link=links['sea']),
        Storage(key='inf', label=_('label_Info'), link=links['inf']),
    ]


def user_location():
    session_info = session.session()
    return session_info.get("lat", ""), session_info.get("lon", "")

def location_indicator():
    return user_location()[1] and "loc_rays" or "location"


class Search:

    def GET(self):
        context = Storage(
            title=_("List of points"),
            status=Storage(
                add="add",
                loc=location_indicator(),  # !!! define better later
                hom="home",
                sea="search",
                inf="info",                 
            ), 
        )

        page_nav_data = Storage(
            nav_data = nav_data(
                add=links.add_point,
                loc=links.place,
                hom=links.home,
                sea=None,
                inf=links.info,
            ),
        )


        context.page_nav_data = page_nav_data

        get_page('search', context)


class Info:

    def GET(self):
        context = Storage(
            title=_("List of points"),
            status=Storage(
                add="add",
                loc=location_indicator(),  # !!! define better later
                hom="home",
                sea="search",
                inf="info",                 
            ), 
        )

        page_nav_data = Storage(
            nav_data = nav_data(
                add=links.add_point,
                loc=links.place,
                hom=links.home,
                sea=links.search,
                inf=None,
            ),
        )


        context.page_nav_data = page_nav_data
        context.about = model.doc_helper(context, "about", i18n.getLanguage())

        get_page('info', context)



class PointList:

    def GET(self):
        user = get_user()

        i = web.input(page="1", order="", 
                lat="", lon="", search_nearby="", topic_id="",
                search="", search_tags="", mode="list")
        page = int(i.page)

        if i.topic_id:
            topics, topic = model.t_helper(i.topic_id)
        else:
            topic = None

        user_lat, user_lon = user_location()
        if not i.search and not i.search_nearby:
            # in absense of search terms, search nearby
            if user_lat:
                i.search_nearby = "1"
                i.lat, i.lon = float(user_lat), float(user_lon)

        if not topic:
            i.setdefault("nearby_radius", config.nearby_radius)
        else:
            i.nearby_radius = None

        points = model.search_helper(i)

        total_num_of_pages = points.num_of_pages(length=config.points_per_page)
        tags = model.tags_helper()

        model.order_helper(points, i.order)

        if i.mode != "map":  # map shows all points, not just one page
            points.limit_by_page(page, length=config.points_per_page)
        points.annotate_by_comments()
        points.annotate_by_tags()
        points.annotate_by_projects()
        points.annotate_by_profiles(default=DEFAULT_POINT_PROFILE)
        if user_lat:
            points.annotate_by_distance(user_lat, user_lon)

        context = Storage(
            title=_("List of points"),
            nearby_radius=i.nearby_radius,
            search=i.search,
            search_nearby=i.search_nearby,
            status=Storage(
                add="add",
                loc=location_indicator(),  # !!! define better later
                hom="home",
                sea="search",
                inf="info",                 
            ), 
        )

        page_nav_data = Storage(
            nav_data = nav_data(
                add=links.add_point,
                loc=links.place,
                hom=None,
                sea=links.search,
                inf=links.info,
            ),
        )


        context.page_nav_data = page_nav_data

        topics_set = set()
        topics_points = []
        topics_dict = {}
        for p in points:
            for t in p.projects:
                if t.id not in topics_set:
                    topics_set.add(t.id)
                    if topic is None or topic.id != t.id:
                        # do not show topic twice
                        topics_points.append(t)
                    topics_dict[t.id] = t
                    t.points = [p]
                else:
                    topics_dict[t.id].points.append(p)

        if topic is not None:
            if topic.id not in topics_set:
                points = []
            else:
                points = topics_dict[topic.id].points

        get_page('point_list', context, points, topics_points, topic)




class Point:

    def GET(self, webinput=None):
        i = webinput or web.input(t_id=None, p_id=None, search="", topic_id=None)

        topics, topic, points, point = model.t_p_helper(i.t_id, i.p_id)
        if not topics:
            print "ERROR"  #!!! should not occur often
            return

        user_lat, user_lon = user_location()
        if user_lat:
            points.annotate_by_distance(user_lat, user_lon)

        context = Storage(
            title=_("Point: details"),
            search=i.get("search", ""),      # for point page
            topic_id=i.topic_id,  # to know where to return to
            status=Storage(
                add="add",
                loc=location_indicator(),  # !!! define better later
                hom="home",
                sea="search",
                inf="info",                 
            ), 
            map_context=Storage(
                zoom=config.mobile_point_zoom + config.getmap_zoomshift, 
                map_width=config.mobile_map_width,
                map_height=config.mobile_map_height,
            ),
        )

        page_nav_data = Storage(
            nav_data = nav_data(
                add=links.add_point,
                loc=links.place,
                hom=links.point_list,
                sea=links.search,
                inf=links.info,
            ),
        )


        context.page_nav_data = page_nav_data

        get_page('point', context, topic, point)


    def POST(self):
        i = web.input(p_id=None, t_id=None, search="", topic_id=None, file={})

        topics, topic, points, point = \
            model.t_p_helper(i.t_id, i.p_id)

        user = get_user()
        if not user:
            print "LOGIN FIRST"  # !!! should never occur
            return

        res = model.store_attachment(point.id, user,
                attach_type="any",
                origin='',
                commenttext="<p>" + i.text + "</p>", 
#                url=i.url, 
#                url_title=i.url_description, 
                fileinfo=i.file)
        self.GET(webinput=i)


class AddPoint:

    def GET(self):

        i = web.input(topic_hint=None)

        user = get_user()
        if user is None:
            Login().GET(webinput=Storage(come_back=links.add_point))
            return

        user_loc = user_location()
        if not user_loc[0]:
            MobileMap().GET()
            return


        context = Storage(
            title=_("List of points"),
            status=Storage(
                add="add",
                loc=location_indicator(),  # !!! define better later
                hom="home",
                sea="search",
                inf="info",                 
            ), 
        )

        page_nav_data = Storage(
            nav_data = nav_data(
                add=None,
                loc=links.place,
                hom=links.home,
                sea=links.search,
                inf=links.info,
            ),
        )

        context.page_nav_data = page_nav_data

        topics_subs = model.Projects(
            by_user_role=(user, "subscribed"))

        topics_highlighted = model.Projects(
            tags=model.Tags("official:highlighted"))

        topics_subs.add(topics_highlighted)

        topics_subs.annotate_by_profiles()
        topics_subs.filter_by_func(acl.authorize.add_point)

        topics_subs.sort_by_title()

        get_page('add_point', context, topics_subs)

    def POST(self):
        presets = i = web.input(file={})

        topics, topic = model.t_helper(presets.topic_id)

        user = get_user()

        # this is security loophole: topic owner
        # can allow contribution without checking captcha
        if not acl.authorize.add_point(topic):  # no login needed
            print "ERROR: user not authorized to add points"
            return


        if "create":  # == True. in case other commands will be added
            user_loc = user_location()
            if not user_loc[0]:
                MobileMap().GET()  #!!! should never happen
                return

            presets.origin = ''
            presets.address = ''
            presets.url = ''
            tags = presets.get("tags", "")
            presets.lat = float(user_loc[0])
            presets.lon = float(user_loc[1])
            model.encode_coordinates(presets)

            point = model.Points.create(
                user=user,
                name=presets.name,
                lat=presets.lat,
                lon=presets.lon,
                url=presets.url,
                origin=presets.origin,
                tags=tags,
                description="<p>" + presets.description.replace("\n", "</p><p>") + "</p>",
                address=presets.address,
                project_id=topic.id,
                fileinfo=i.file,
            )

            web.seeother(links("point", t_id=topic.id, p_id=point.id))
            return



class MapAction:
    def GET(self, c_lat, c_lon, zoom, map_width, map_height):
        x = int(int(map_width)/2)
        y = int(int(map_height)/2)
        for k in web.input():
            if "," in k:
                x, y = map(int, k.split(","))

        # !!! refactor
        if config.getmap_custom_wms == "wms":
            lat, lon = mobile_map.click_coord_hybrid(x, y, 
                c_lat=float(c_lat), c_lon=float(c_lon), 
                zoom=float(zoom), mapx=int(map_width), mapy=int(map_height))
        else:
            lat, lon = mobile_map.click_coord_hybrid_osm(x, y, 
                c_lat=float(c_lat), c_lon=float(c_lon), 
                zoom=float(zoom), mapx=int(map_width), mapy=int(map_height))

        MobileMap().GET(webinput=Storage(lat=str(lat), lon=str(lon), zoom=str(zoom)))


class MobileMap:
    def GET(self, webinput=None):
        i = webinput or web.input(lat=None,
                      lon=None,
                      zoom=None,
                      gps=None,
                      address=None,
                      )

        if i.get("gps", ""):
            i.zoom = float(i.zoom or (config.mobile_gps_zoom + config.getmap_zoomshift))
        else:
            i.zoom = float(i.zoom or (config.mobile_zoom + config.getmap_zoomshift))

        user = get_user()

        if user is None:
            user1, msg = autologin(i)
            if user1 is not None:
                user = user1

        location = None

        user_lat, user_lon = user_location()

        if user_lat:
            location_hint = \
                Storage(lat=float(user_lat),
                        lon=float(user_lon),
                        id=1,
                     )
        else:
            location_hint = \
                Storage(lat=float(config.center_lat),
                        lon=float(config.center_lon),
                        id=1,
                     )


        address_lookup = ""
        if i.get("address", ""):
            location = Storage(id=0, zoom=float(config.mobile_zoom)+config.getmap_zoomshift)
            metadata = {'hint_lat': location_hint.lat,
                        'hint_lon': location_hint.lon,}
            location.update(
                model.geocoding_helper(i.address, 
                    onfail=('', ''), 
                    metadata=metadata)
            )
            if not location.lat:
                location = None
                address_lookup = "failed"
            else:
                i.zoom = location.get("zoom", float(config.mobile_zoom)+config.getmap_zoomshift)
                address_lookup = "success"
        if not location and i.lat and i.lon:
            location = \
                Storage(lat=float(i.lat.replace(",", ".")),
                        lon=float(i.lon.replace(",", ".")),
                        id=0,
                         )

        if "forget" in i:
            session.remove_info(dict(lat=None, 
                                lon=None,
                                zoom=None))
            web.seeother(links.map)
            return
        elif "submit" in i and location:
            # set location
            session.update_info(dict(lat=float(location.lat or 0), 
                                lon=float(location.lon or 0),
                                zoom=int(i.zoom) - config.getmap_zoomshift))

            web.seeother(links.point_list)
            return

        if not location:
            location = location_hint

        model.encode_coordinates(location)

        if config.getmap_custom_wms == "wms":
            map_context = mobile_map.MapContextHybrid(
                    lat=location.lat,
                    lon=location.lon,
                    zoom=int(float(i.zoom)),
                    links=links,
                    map_width=config.mobile_map_width,
                    map_height=config.mobile_map_height,
            )
        else:
            map_context = mobile_map.MapContextHybridOSM(
                    lat=location.lat,
                    lon=location.lon,
                    zoom=int(float(i.zoom)),
                    links=links,
                    map_width=config.mobile_map_width,
                    map_height=config.mobile_map_height,
            )

        map_context.tile_id = "%(lat)s,%(lon)s,%(zoom)s,%(map_width)s,%(map_height)s" % map_context

        context = Storage(
            title=_("User location"),
            address=i.get("address", ""),
            address_lookup=address_lookup,
            status=Storage(
                add="add",
                loc=location_indicator(),  # !!! define better later
                hom="home",
                sea="search",
                inf="info",                 
            ),
            map_context=map_context,
        )
        if "gps" in i:
            context.gps = i.gps

        page_nav_data = Storage(
            nav_data = nav_data(
                add=links.add_point,
                loc=None,
                hom=links.home,
                sea=links.search,
                inf=links.info,
            ),
        )


        context.page_nav_data = page_nav_data

        get_page('map', context, location)

    POST = GET

class Login:
    def POST(self, webinput=None):
        i = webinput or web.input()
        user, msg = autologin(i)

        context = Storage()

        if not user:
            get_page('login', context, come_back=i.get('come_back', ''))
            return
        if user.username:
            if "come_back" in i:
                web.seeother(i.come_back)
            else:
                web.seeother(links.map)
            return

    GET = POST

class Logout:
    def POST(self):
        unbind_user()
        web.seeother(links.info)

    GET = POST


Index = MobileMap
