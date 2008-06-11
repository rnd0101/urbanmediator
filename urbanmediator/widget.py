# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Widget controller.

    To add new widget several places should be edited
    (in links.py, code.py, widgetize.py and here in widget.py,
    plus templates/widget/YOURWIDGET.html and
    templates/pc/topic_tools.html)

    See `topic_links` as example.

"""

import re

import web
from web.utils import Storage

import model
import media
import util
import i18n
import config
import turing
import url_handler
import webutil
import mobile_map
import view
from view import widget_render as render, get_widget, pc_macro as macros
from profiles import *
from links import widget_links as links, pc_links, feed_links
from webutil import request_uri, dispatch_url
import webform as form
#from session_user import *

_ = i18n._

urls = (
    '/topic/(.+)/topic_points', 'TopicPoints',
    '/topic/(.+)/topic_links', 'TopicLinks',
    '/topic/(.+)/submit', 'SubmitWidget',
    '/topic/(.+)/note', 'NoteWidget',
    '/topic/(.+)/map', 'MapWidget',
    '/topic/.+/container', 'ContainerWidget',
)


def url_to_class(url):
    #!!! ugly now. Use regexps for urls above
    if "/submit" in url:
        return SubmitWidget
    elif "/note" in url:
        return NoteWidget
    elif "/container" in url:
        return ContainerWidget
    elif "/topic_points" in url:
        return TopicPoints
    elif "/topic_links" in url:
        return TopicLinks
    elif "/map" in url:
        return MapWidget

def render_widget(text):
    try:
        m = re.search(r'src="(.+?)"', text).groups()[0]
    except:
        return "[ERROR with this widget]"

    if getattr(url_to_class(m), "ALWAYS_IFRAME", False):
        return text

    return get_widget_code(m)

def get_widget_url(text):
    try:
        return re.search(r'src="(.+?)"', text).groups()[0]
    except:
        return ""

def dictify(fs): return dict([(k, fs[k]) for k in fs.keys()])

def get_widget_code(path, mapping=urls, prefix="/widget"):
    """
    Based on handle in web.py's request.py 
    Simplified to work only for the current module.
    """
    return webutil.dispatch_url(path, globals(), mapping, prefix)

web.template.Template.globals.update(dict(
    widget_links=links,
    render_widget=render_widget,
    get_widget_code=get_widget_code,
    get_widget_url=get_widget_url,
))



class SubmitWidget:
    def GET(self, topic_id, onlycode=False, webinput=None):
        presets = webinput or web.input()
        try:
            presets.referer = web.ctx.environ["HTTP_REFERER"]
        except KeyError:
            presets.referer = 0

        ### compat only !!! remove 
        if "disabled_text" not in presets:
            presets.disabled_text = _("Point addition disabled.")
        ###

        context = Storage(
            presets=presets,
            offset = 14,
            framed = 0,
            onlycode=onlycode,
            title=presets.get("title", _("Add point")),
            desturl=pc_links("topic_newpoint", int(topic_id), **presets),
            submitform=pc_links("topic_newpoint", int(topic_id)),
        )

        topics, topic = model.t_helper(topic_id)

        if onlycode:
            presets.referer = ''
            return get_widget('submit', context, topic, presets)

        get_widget('submit', context, topic, presets)


class NoteWidget:
    def GET(self, topic_id, onlycode=False, webinput=None):
        presets = webinput or web.input()
        try:
            presets.referer = web.ctx.environ["HTTP_REFERER"]
        except KeyError:
            presets.referer = 0

        context = Storage(
            presets=presets,
            offset=14,
            framed=0,
            onlycode=onlycode,
            title=presets.get("title", _("Note")),
        )

        topics, topic = model.t_helper(topic_id)

        if onlycode:
            presets.referer = ''
            return get_widget('note', context, topic, presets)

        get_widget('note', context, topic, presets)


class MapWidget:

    ALWAYS_IFRAME = 1

    def GET(self, topic_id, onlycode=False, webinput=None):

        presets = webinput or web.input()
        try:
            presets.referer = web.ctx.environ["HTTP_REFERER"]
        except KeyError:
            presets.referer = 0

        context = Storage(
            presets=presets,
            offset = 10,
            framed = 1,
            onlycode=onlycode,
            title=presets.get("title", _("Points")),
            desturl=pc_links("topic", int(topic_id), **presets),
#            submitform=pc_links("topic_newpoint", int(topic_id)),
        )

        topics, topic = model.t_helper(topic_id)

        topics.annotate_by_datasources()
        topics.annotate_by_points()

        number_of_points = int(presets.get("number_of_points",
            config.points_per_page))

        points = model.Points(project=topic, external=None)
        points.limit_by_page(1, length=number_of_points)
        points.annotate_by_comments()
        points.annotate_by_tags()
        points.annotate_by_profiles(default=DEFAULT_POINT_PROFILE)

        feed_link = feed_links("topic_points",
            topic.id, presets, page=None)

        if "zoom" in topic.profile and topic.profile.zoom != "auto":
            c_lat, c_lon, c_zoom = \
                topic.lat, topic.lon, topic.profile.zoom
            c_zoom = int(c_zoom)
        else:
            c_lat, c_lon, c_zoom = points.central_point(
                config.center_lat, config.center_lon, 14)

        map_context = Storage(
            getmap_url=pc_links.getmap,
            getmap_layers=config.getmap_layers,
            getmap_layers1=config.getmap_layers1,
            getmap_layers2=config.getmap_layers2,
            map_params=config.getmap_params,
            getmap_custom=config.getmap_custom,
            getmap_custom_init=config.getmap_custom_init,
            lat=c_lat,
            lon=c_lon,
            zoom=c_zoom + config.getmap_zoomshift,
            initial_feed=feed_link,
            has_new_point="false",
            getmap_zoom1=config.getmap_zoom1 + config.getmap_zoomshift,
            getmap_zoom2=config.getmap_zoom2 + config.getmap_zoomshift,
        )
        model.encode_coordinates(map_context)

        context.map_context = map_context
        context.page_specific_js = macros.map_js(map_context)

        if onlycode:
            presets.referer = ''
            # !!! map widget can't be part of combo
            self_link = links('map', topic_id, **presets)
            return """<iframe src="%s" style="height:%spx;width:%spx;border:none;"></iframe>""" % \
                (self_link, presets.height, presets.width)


        get_widget('map', context, topic, presets)


class TopicPoints:
    def GET(self, topic_id, onlycode=False, webinput=None):

        presets = webinput or web.input()
        try:
            presets.referer = web.ctx.environ["HTTP_REFERER"]
        except KeyError:
            presets.referer = 0

        context = Storage(
            presets=presets,
            offset = 10,
            framed = 1,
            onlycode=onlycode,
            title=presets.get("title", _("Points")),
            desturl=pc_links("topic", int(topic_id), **presets),
#            submitform=pc_links("topic_newpoint", int(topic_id)),
        )

        topics, topic = model.t_helper(topic_id)

#        if not topics:
#            web.seeother(links("index", message=_("No such topic. Update your bookmarks.")))
#            return

        topics.annotate_by_datasources()
        topics.annotate_by_points()

        number_of_points = int(presets.get("number_of_points",
            config.points_per_page))

        points = model.Points(project=topic, external=None)
        
        model.order_helper(points, presets.get('order', 
            config.main_page_point_orders[0]))

        points.limit_by_page(1, length=number_of_points)
        points.annotate_by_comments()
        points.annotate_by_tags()
        points.annotate_by_profiles(default=DEFAULT_POINT_PROFILE)


        if onlycode:
            presets.referer = ''
            return get_widget('topic_points', context, presets, points, topic)

        get_widget('topic_points', context, presets, points, topic)


class TopicLinks:
    def GET(self, topic_id, onlycode=False, webinput=None):

        presets = webinput or web.input()
        try:
            presets.referer = web.ctx.environ["HTTP_REFERER"]
        except KeyError:
            presets.referer = 0

        context = Storage(
            presets=presets,
            offset = 10,
            framed = 1,
            onlycode=onlycode,
            title=presets.get("title", _("Links")),
            desturl=pc_links("topic", int(topic_id), **presets),
        )

        topics, topic = model.t_helper(topic_id)

        topics.annotate_by_datasources()
        topics.annotate_by_points()

        number_of_points = int(presets.get("number_of_links",
            config.links_per_page))

        if onlycode:
            presets.referer = ''
            return get_widget('topic_links', context, presets, topic)

        get_widget('topic_links', context, presets, topic)



MAX_NUMBER_OF_ITEMS_IN_CONTAINER = 10

class ContainerWidget:
    def GET(self, onlycode=False, webinput=None):
        presets = webinput or web.input()
        try:
            presets.referer = web.ctx.environ["HTTP_REFERER"]
        except KeyError:
            presets.referer = 0
        context = Storage(
            presets=presets,
            offset = 14,
            framed = 0,
            onlycode=onlycode,
            title=presets.get("title", _("Add point")),
        )

        widget_urls = []
        for n in range(MAX_NUMBER_OF_ITEMS_IN_CONTAINER):
            urln = "u%i" % n
            if urln in presets:
                widget_urls.append(presets[urln])

        if onlycode:
            presets.referer = ''
            return get_widget('container', context, presets, widget_urls)

        get_widget('container', context, presets, widget_urls)

