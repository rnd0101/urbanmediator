# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Controller for all feed-related views 
    including ATOM, OPML, LMX, KML, sitemap, ...

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
import feed_data
import csv_report
import view
import acl
from view import feed_render as render, get_feed
from profiles import *
from links import feed_links as links, pc_links
from webutil import request_uri
from session_user import *

_ = i18n._

urls = (
    '/opml.xml', 'OPML',
    '(?:/?)(kml|lmx|)/topics', 'Topics',
    '(?:/?)(kml|lmx|json|)/search', 'Search',
    '/opensearch.xml', 'OpenSearch',
    '(?:/?)(kml|lmx|)/topic/(\d+)/points', 'Topic_points',
    '(?:/?)(kml|lmx|)/topic/(\d+)/point/(\d+)/comments', 'Point_comments',
    '/user/([^/]+)/topics', 'User_topics',
    '/topic/(\d+).csv', 'Topic_as_csv',
    '/file', 'IncomingFile',
    '/mailto', 'MailTo',
    '/address', 'Address',
    '/topic/(\d+)', 'IncomingEntry',
)

web.template.Template.globals.update(dict(
    feed_links=links,
))

feed_content_type = Storage(
  atom="application/atom+xml",
  atomserv="application/atomsvc+xml",
  kml="application/vnd.google-earth.kml+xml",
  lmx="application/vnd.nokia.landmarkcollection+xml; charset=utf-8"
)

def get_feed_helper(context, objects, summary, link, format='', with_content=None):
    i = web.input(ol='')  # if this parameter set, it means OpenLayers
    format = format or 'atom'
    technical_feed = (i.ol == "1")
    if with_content is None:
        with_content = not technical_feed  # and openlayers get HTML in summary
    web.header("content-type", feed_content_type[format])
    for p in objects:
        p.url = link(p)
        if technical_feed:
            # !!! multicoordinate hack
            model.encode_coordinates(p)
            p.lat = p.repr_lat
            p.lon = p.repr_lon
            #
        try:
            p.summary = summary(p)
            p.summary = view.render_text(p.summary)
        except:
            if "summary" not in p:
                p.summary = _("No description")
    context.setdefault("title", model.UM.title())
    context.setdefault("subtitle", model.UM.title())
    if format == 'atom':
        if with_content:
            get_feed(context, template_name="feed_with_content", items=objects)
        else:
            get_feed(context, items=objects)
    elif format == 'kml':
        get_feed(context, template_name="kml", items=objects)
    elif format == 'lmx':
        get_feed(context, template_name="lmx", items=objects)


class Sitemap:

    def GET(self):
        categories = model.Categories()
        categories.annotate_by_projects()
        for category in categories:
            category.projects.annotate_by_comments()
            category.projects.annotate_by_points()

        context = Storage()
        print render.sitemap(context, categories)

class OpenSearch:

    def GET(self):
        context = Storage()
        web.header("content-type", 'application/opensearchdescription+xml')
        print render.opensearch(context)

class OPML:

    def GET(self):
        categories = model.Categories()
        categories.annotate_by_projects()
        for category in categories:
            category.projects.annotate_by_comments()
            category.projects.annotate_by_points()

        context = Storage()
        print render.opml(context, categories)

class Address:
    """
    """
    def GET(self):
        i = web.input(address="")
        i.update(model.geocoding_helper(i.get("address", ""), onfail=('', '')))
        if not i.lat:
            print "error"
        else:
            print i.lat, i.lon

class FeedEntry:
    """
        Proxy for en external point so it can be shown on the map

    """
    def GET(self, format, tags, command):
        if format == "atom/":
            context = Storage(self_url=request_uri(),)
            web.header("content-type", "application/atom+xml")
            # proxying feed point
        i = web.input()
        datasources = model.Datasources(id=i.ds)
        ds = datasources.list()[0]
        feed_url = ds.url
        points = model.Points(internal=None, external=[feed_url])
        points.filter_by_uuid(i.uuid)
        points.annotate_by_tags()
        for p in points:
            p.summary = _("No summary")  # !!!

        points.last_activity()
        context.title = ds.description
        context.subtitle = _("from external sources")
        get_feed(context, items=points)
        return

class Topic_points:

    def GET(self, format, topic_id):

        i = web.input(order="", search="", search_tags="", ol="")

        topics, topic = model.t_helper(topic_id)
        if not topics:
            # web.seeother(links("index", message=_("No such topic. Update your bookmarks.")))
            # ???
            return

        points = model.search_helper(i, topic)
        model.order_helper(points, i.order)

        points.annotate_by_comments()
        points.annotate_by_tags()
        points.annotate_by_profiles(default=DEFAULT_POINT_PROFILE)

        context = Storage(
            title=_("Topic points"),
        )

        points.last_activity()
        
        get_feed_helper(context, points,
            summary=lambda p: p.comments.list()[0].text,
            link=lambda p: pc_links('point', topic.id, p.id),
            format=format,
            with_content=(not i.ol),
        )


class Topic_as_csv:

    def GET(self, topic_id):
        topics, topic = model.t_helper(topic_id)

        if not topics:
            # web.seeother(links("index", message=_("No such topic. Update your bookmarks.")))
            # ???
            return

        points = model.Points(project=topic, external=None)
        points.annotate_by_comments()
        points.annotate_by_tags()
        points.annotate_by_profiles(default=DEFAULT_POINT_PROFILE)

        web.header("content-type", 
                   "text/csv; charset=utf-8; header=present")
        import codecs
        print codecs.BOM_UTF8 + csv_report.report(points)

class Point_comments:
    def GET(self, format, topic_id, point_id):
        i = web.input(ol="")
        topics, topic, points, point = model.t_p_helper(topic_id, point_id)
        if not topics:
            redirect(5, _("No such topic. Delete from your bookmarks: ") + request_uri(), 
                links.index)
            return

        if not points:
            redirect(5, _("No such point. Delete from your bookmarks: ") + request_uri(), 
                links("topic", topic.id))
            return

        points.annotate_by_comments()

        comments = point.comments
        comments.annotate_by_profiles(default=DEFAULT_COMMENT_PROFILE)

        context = Storage(
            title=_("Point: ") + point.title,
        )

        comments.last_active = point.added
        for c in comments:
            comments.last_active = max(comments.last_active, c.added)
            c.title = util.first_line(c.text, length=64)
            c.summary = c.text
            c.tags = []

        uri_pref = pc_links('point', topic.id, point.id) + "#comment"
        get_feed_helper(context, comments,
            summary=lambda c: c.summary,  #???
            link=lambda c: uri_pref + str(c.id),
            format=format,
            with_content=(not i.ol))


class Topics:

    def GET(self, format):
        topics = model.Projects()
        topics.sort_by_vitality()
        topics.last_activity()

        topics.annotate_by_tags()
        topics.annotate_by_comments()
        topics.annotate_by_latest_points()
        # topics.annotate_by_profiles(default=DEFAULT_TOPIC_PROFILE)

        context = Storage(
            title = _("Topics"),
        )

        get_feed_helper(context, topics,
            summary=lambda t: t.comments.list()[0].text,
            link=lambda t: pc_links('topic', t.id),
            format=format,
        )

class User_topics:

    def GET(self, username):
        # auth?

        try:
            users = model.Users(username=username)
            user = users.list()[0]
        except:
            context = Storage(title=_("No such user"))
            print render.collections(context, [])
            return

        topics_subs = model.Projects(
            by_user_role=(user, "subscribed"))
#        topics_subs.annotate_by_profiles(default=DEFAULT_TOPIC_PROFILE)
#        topics_subs.annotate_by_points()
#        topics_subs.annotate_by_comments()


        topics_highlighted = model.Projects(
            tags=model.Tags("official:highlighted"))
#        topics_highlighted.annotate_by_profiles(default=DEFAULT_TOPIC_PROFILE)
#        topics_highlighted.annotate_by_latest_points()
#        topics_highlighted.annotate_by_comments()

        topics_subs.add(topics_highlighted)
        topics_subs.sort_by_title()

        context = Storage(title=_("User") + " " + username,)
        web.header("content-type", feed_content_type['atomserv'])
        print render.collections(context, topics_subs)


class Search:

    def GET(self, format):
        i = web.input(order="", search="", search_tags="", ol="")

        user = get_user()

        points = model.search_helper(i)
        model.order_helper(points, i.order)

        points.annotate_by_comments()
        points.annotate_by_projects()
        points.annotate_by_tags()

        context = Storage(
            title=_("Search for '%s'") % i.search,
        )

        points.last_activity()

        if format != 'json':
            get_feed_helper(context, points,
                summary=lambda p: p.comments.list()[0].text,
                link=lambda p: pc_links('point', p.first_project.id, p.id),
                format=format,
                with_content=(not i.ol))
            return
        else:
            import simplejson_encoder
            print simplejson_encoder.JSONEncoder(indent=2).encode(json_structure(points))
            return

def json_structure(points):
    json = []
    for point in points:
        topic = point.first_project
        if topic is None:
            continue
        json.append({"info": dict(
           point_id=point.id,
           point_name=point.title,
           href_point_page=pc_links('point', topic.id, point.id),
           date_creation=view.rel_date(point.added),
           creator_user_id=point.user_id,
           creator_user_name=point.author,
           lon=point.repr_lon,
           lat=point.repr_lat,
        ),
        "content": dict(
           textual=point.first.text,
           images=[],
        ),
        "tags": point.tags.for_str().split(" "),
        "topics":
            [dict(
                topic_id=topic.id,
                topic_name=topic.title,
                href_topic_page=pc_links('topic', topic.id),
                ),
            ],
        })
    return json


def unauthorized(realm):
    """Set a 401 Unauthorized status with the given realm.
    """
    web.ctx.status = '401 Unauthorized'
    web.header('WWW-Authenticate', 'WSSE realm="%s", profile="UsernameToken"' % realm)

def created(location):
    web.ctx.status = '201 Created'
    web.header('Location', location)


def internal_error():
    web.ctx.status = '500 Internal Server Error'

def forbidden():
    web.ctx.status = '403 Forbidden'

class MailTo:
    def POST(self):
        """default mailto handler"""
        i = web.input()

        p = model.store_message_to_point_and_comments(i.Mail, 
            acl.authorize.add_point_by_user)

        if p is not None:
            print p.id
        else:
            print "SENDING FAILED"


def get_slug():
    return web.ctx.env.get("HTTP_SLUG", "noname")

class IncomingFile:
    """Atom publishing handler for incoming mediafile"""
    def POST(self):
        #1 authenticate
        user = get_wsse_user()
        if user is None:
            unauthorized('um')
            return

        #2 store file and get key to it
        try:
            media_url = None
            fc = web.webapi.data()

            if fc:
                try:
                    ct = web.ctx.env.get("CONTENT_TYPE", "application/octet-stream").split(",")[-1].strip()
                except:
                    ct = "image/jpeg"

                try:
                    fn = get_slug()
                except:
                    fn = "aaa.jpg"

                media_url = config.base_url + \
                    media.uploadMediaFile(fc,
                        filename=fn,
                        content_type=ct,
                    )
        except:
            pass

        #3 reply if file successfully stored
        if media_url:
            created(media_url)
        else:
            internal_error()

class IncomingEntry:
    """Atom publishing handler for incoming entry"""
    def POST(self, topic_id):
        
        #1a
        # wsse auth
        # user = ...
        user = get_wsse_user()
        if user is None:
            unauthorized('um')
            return

        topics, topic = model.t_helper(topic_id)
        if not topics:
            web.notfound()
            return

        # 1b authorize
        if not acl.authorize.add_point(topic):
            forbidden()
            return

        #2 parse XML and store the point
        fc = web.webapi.data()
        entry = model.Point(feed_data.parse_entry(fc))

        point = model.Points.create(
                user=user,
                name=entry.title,
                lat=entry.lat,
                lon=entry.lon,
                url='',
                origin='',
                tags=entry.tags,
                description=entry.description,
                address='',
                project_id=topic_id,
            )

        created(pc_links("point", topic_id, point.id))

