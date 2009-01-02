# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Main controller.
"""

import time, os, urllib, sys, re

import web
from web.utils import Storage

import config

import model
import session
import media
import turing
import i18n
import userbase
import view
import acl
from profiles import *
from links import pc_links as links, feed_links, mobile_links
from webutil import request_uri
import session_user
from session_user import *

import feed, mobile, widget
from feed import Sitemap

from view import pc_macro as macros, pc_render as render, \
                pc_get_page as get_page

import webform as form

import util
import url_handler

_ = i18n._

def folder(module, prefix=None):
    import urbanmediator
    urls_tuple = getattr(urbanmediator, module).urls
    prefix = "/" + (prefix or module)
    return tuple([(i % 2) and ("urbanmediator." + module + "." + v) or (prefix + v)
                  for i, v in enumerate(urls_tuple)])

urls = folder('mobile') \
    + folder('feed') \
    + folder('widget') + (
    '/', 'Index',
    '/media', 'Media',
    '/(favicon.ico)', 'StaticMedia',
    '/Static/(.*)', 'StaticMedia',
    '/index.html', 'Index',
    '/search.html', 'Search',
    '/map_search.html', 'MapSearch',
    '/sitemap.xml', 'Sitemap',
    '/skindemo', 'Skindemo',
    '/selftest', 'Selftest',
    '/login.html', 'Login',
    '/logout.html', 'Logout',
    '/(about|privacy|contact).html', 'Doc',
    '/(help).html', 'StaticDoc',
    '/guide/(help_[A-Z0-9a-z_]+).html', 'Guide',
    '/guide/([A-Z0-9a-z_]+[.](?:png|gif|jpg))', 'GuideObject',
    '/feedback', 'Feedback',
    '/setlang', 'SetLanguage',
    '/settings.html', 'Settings',
    '/edit_doc.html', 'EditDoc',
    '/getmap', 'GetMapFast',
    '/turing/(CAPTCHAS/[A-Za-z0-9]+)', 'Turing',
    '/user/(.+)/tools', 'User_tools',
    '/user/(.+)/settings', 'User_settings',
    '/user/(.+)/location', 'User_location',
    '/user/(.+)', 'User',
    '/topic/(\d+)', 'Topic',
    '/topic/([0-9]+)/point/([0-9]+)', 'Point',
    '/topic/([0-9]+)/point/([0-9]+)/addtag', 'Point_addtag',
    '/topic/([0-9]+)/point/([0-9]+)/delete', 'Point_delete',
    '/topic/([0-9]+)/point/([0-9]+)/addcomment', 'Point_addcomment',
    '/topic/([0-9]+)/point/([0-9]+)/settings', 'Point_settings',
    '/topic/([0-9]+)/point/([0-9]+)/comment/([0-9]+)/edit', 'Point_editcomment',
    '/topic/([0-9]+)/point/([0-9]+)/comment/([0-9]+)/delete', 'Point_deletecomment',

    '/topic/([0-9]+)/tools/submit_widgetize', 'urbanmediator.widgetize.SubmitWidgetize',
    '/topic/([0-9]+)/tools/note_widgetize', 'urbanmediator.widgetize.NoteWidgetize',
    '/topic/([0-9]+)/tools/topic_points_widgetize', 'urbanmediator.widgetize.TopicPointsWidgetize',
    '/topic/([0-9]+)/tools/topic_links_widgetize', 'urbanmediator.widgetize.TopicLinksWidgetize',
    '/topic/([0-9]+)/tools/container_widgetize', 'urbanmediator.widgetize.ContainerWidgetize',
    '/topic/([0-9]+)/tools/map_widgetize', 'urbanmediator.widgetize.MapWidgetize',
    '/topic/([0-9]+)/tools/widget_editor', 'urbanmediator.widgetize.WidgetEditor',
    '/topic/([0-9]+)/tools/widget_move', 'urbanmediator.widgetize.WidgetMove',
    '/topic/([0-9]+)/subscription', 'Topic_subscription',

    '/topic/([0-9]+)/tools/widgets', 'Topic_widgets',
    '/topic/([0-9]+)/comment/([0-9]+)/delete', 'Topic_deletecomment',
    '/topic/([0-9]+)/comment/([0-9]+)/edit', 'Topic_editcomment',

    '/topic/([0-9]+)/ds/([0-9]+)/edit', 'Datasource_edit',
    '/topic/([0-9]+)/ds/([0-9]+)/delete', 'Datasource_delete',
    '/topic/([0-9]+)/tools/feed_import', 'FeedImport',
    '/topic/([0-9]+)/addwidget', 'Topic_addwidget',
    '/topic/([0-9]+)/addtrigger', 'Topic_addtrigger',
    '/topic/([0-9]+)/trigger/([0-9]+)/delete', 'Trigger_delete',
    '/topic/([0-9]+)/trigger/([0-9]+)/edit', 'Trigger_edit',
    '/topic/([0-9]+)/adminlist', 'Topic_adminlist',
    '/topic/([0-9]+)/tools', 'Topic_tools',
    '/topic/([0-9]+)/widgets', 'Topic_widgets',
    '/topic/([0-9]+)/delete', 'Topic_delete',
    '/topic/([0-9]+)/settings', 'Topic_settings',
    '/topic/([0-9]+)/feedback', 'Topic_feedback',
    '/topic/([0-9]+)/advanced', 'Topic_advanced',
    '/topic/([0-9]+)/location', 'Topic_location',
    '/newtopic.html', 'NewTopic',
    '/topic/([0-9]+)/new_point', 'Topic_newpoint',
    '/signup.html', 'Signup',
    '/redirect.html', 'Redirect',
    '/alert.html', 'Alert',
)

class Redirect:
    def GET(self, *args, **kwargs):
        i = web.input(message="", url=links.index, t="")
        if not i.t:
            i.t = max(min(3, len(i.message) / 20), 10)
        context = Storage(timeout=i.t)
        print render.redirect(context, i.message, i.url, cache=config.cache)
    POST = GET

def redirect(timeout, msg, url):
    web.seeother(links("redirect", message=msg, url=url, t=timeout))

class Alert:
    def GET(self, *args, **kwargs):
        i = web.input(message="", url1="", m1=_("Yes"), 
                                  url2=links.index, m2=_("Cancel"))
        actions = []
        for a in range(1, 10):
            url = i.get("url"+str(a), None)
            m = i.get("m"+str(a), None)
            if m and url:
                actions.append(model.Storage(url=url, message=m))
            else:
                break

        context = Storage()
        print render.alert(context, i.message, actions, cache=config.cache)
    POST = GET

# methods to associate the user with the http session:

def process_login_result(i):
    """ Logs user in
    """
    user_word = i.get("user_word", "")
    captcha_key = i.get("captcha_key", "CAPTCHAS/no")

    user = None
    if i.username or i.password:
        credentials = Storage(username=i.username,
                              password=i.password)
        user = userbase.authenticate(credentials)
        if user:
            turing.drop_captcha(captcha_key)
            return user, "logged in"

    if not i.user_word.strip():
        turing.drop_captcha(captcha_key)
        return None, _("Login failed")

    captcha_test = turing.check_captcha(captcha_key, user_word)
    if captcha_test:
        model.del_by_captcha(captcha_key)
        return None, _("Visual code is wrong. Try again")

    users = model.Users(description=captcha_key)
    if not users:
        return None, _("No such user - error occured")

    user = users.first_item()
    model.update_user_description(user, "guests")
    return user, "logged in"

def login_through(*args, **kwargs):
    """ Usage pattern:
        def GET(self, ...):
            user = login_through()
            if not user: return

    """

    login_level = kwargs.get("level", "visitors")   # visitors OR registered

    # Already logged in:
    user = get_user()  # XXX still hole here
    if user:
        if login_level == "registered" and "guests" in user.groupnames:
            unbind_user()
            pass  # should login again
        else:
            return user

    i = web.input(username='', password='', 
                captcha_key='', user_word='')

    msg = ""
    if i.password or i.captcha_key or i.user_word:
        user, msg = process_login_result(i)
        if user:
            bind_user(user)
            return user

    hint_users = model.Users(username=i.username)
    show_visitor_login = len(hint_users) == 0 \
                        and login_level == "visitors"

    if not i.has_key("came_from"):
        i.came_from = kwargs.get("came_from", request_uri())

    context = Storage(
            username_hint=i.username,
            show_visitor_login=show_visitor_login,
            message=msg,
            title=_("Login page")
    )

    if kwargs.get("post_login", False):
        context.method = "POST"
        context.form_action = links.login
    else:
        context.method = web.ctx.method
        context.form_action = i.came_from

    if show_visitor_login:
        context.captcha_key = captcha_key = turing.new_captcha()
        context.captcha_url = config.base_url + "/turing/" + captcha_key

        credentials = Storage(username=userbase.get_visitor_username(),
            password=None, description=captcha_key)

        group = model.Groups("guests").first_item()

        user = userbase.add_user(credentials, None, group=group)  # no profile yet

    del i.username, i.user_word, i.captcha_key, i.password
    if "file" in i:
        del i.file

    get_page('login', context, user, i)
    return None

def auto_author_user(feed_author, user):
    username = userbase.get_feed_username(feed_author)
    users = model.Users(username=username)
    if users:
        feed_user = users.first_item()
    else:
        group = model.Groups("guests").first_item()
        credentials = Storage(username=username, password=None, description="externals")
        feed_user = userbase.add_user(credentials, None, group=group)
    if feed_user is None:
        feed_user = user   #!!! should never happen!!!
    return feed_user

def auto_anonymous_user():
    """Creates one-timedummy user for contributions' authors bypassed Turing test """

    # session ensures that username will be the same for the session
    username = userbase.get_anonymous_username()

    credentials = Storage(username=username, password=None, description="auto")

    group = model.Groups("guests").first_item()

    return userbase.add_user(credentials, None, group=group)  # no profile yet

def get_user_groups():
    user = get_user()

    if user is None:
        return ["anonymous"]

    return [g.groupname for g in user.groups]

def user_belongs_to(groupnames):
    """use:  user_belongs_to("users,guests")
    """
    return set(get_user_groups()) \
        & set([x.strip() for x in groupnames.split(",")])


def thumbnail_upload(fileinfo, maxx, maxy):
    """Senses file upload, makes priview from that,
    stores it and gives /media URL"""
    media_url = ""
    if not fileinfo.file:
        return media_url
    fc = fileinfo.file.read()
    if fc:
        try:
            media_url = media.uploadMediaFileThumbnail(
                        fc, 
                        filename=fileinfo.filename,
                        maxx=maxx, maxy=maxy,
                        )
        except:
            pass
    return media_url


def set_map_context(context, center, zoom, initial_feed='',
        has_new_point=False, topic=None):
    """Map context helper. Helps keep map-related data 
    in one place.
    If map per topic will be implemented, more config parameters
    will be needed.
    """
    if topic is not None and "getmap_params" in topic.profile \
            and topic.profile.getmap_params:
        topic_profile = topic.profile
        map_context = Storage(
            getmap_custom=1,   #!!!
            getmap_custom_init=topic_profile.getmap_custom_init,
            getmap_url=links.getmap,
            getmap_layers=topic_profile.getmap_layers,
            getmap_layers1=topic_profile.getmap_layers1,
            getmap_layers2=topic_profile.getmap_layers2,
            getmap_zoom1=int(topic_profile.getmap_zoom1) + int(topic_profile.getmap_zoomshift),
            getmap_zoom2=int(topic_profile.getmap_zoom2) + int(topic_profile.getmap_zoomshift),
            map_params=topic_profile.getmap_params,
            lat=center[0],
            lon=center[1],
            zoom=int(zoom) + int(topic_profile.getmap_zoomshift),
            initial_feed=initial_feed,
            has_new_point=has_new_point and "true" or "false",
        )
    else:
        map_context = Storage(
            getmap_url=links.getmap,
            getmap_custom=config.getmap_custom,
            getmap_custom_init=config.getmap_custom_init,
            getmap_layers=config.getmap_layers,
            getmap_layers1=config.getmap_layers1,
            getmap_layers2=config.getmap_layers2,
            getmap_zoom1=config.getmap_zoom1 + config.getmap_zoomshift,
            getmap_zoom2=config.getmap_zoom2 + config.getmap_zoomshift,
            map_params=config.getmap_params,
            lat=center[0],
            lon=center[1],
            zoom=int(zoom) + config.getmap_zoomshift,
            initial_feed=initial_feed,
            has_new_point=has_new_point and "true" or "false",
        )
    model.encode_coordinates(map_context)

    context.map_context = map_context
    context.geocoding_example = model.geocoding_example()
    context.page_specific_js = macros.map_js(map_context)


def page_nav_pack(i, total_num_of_pages,
                  linkstr="", link_params=None,
                  orders=None, 
                  modes=None):
    link_params = link_params or [{}]
    orders = orders or []
    modes = modes or []

    page = int(i.page)

    nav_data = Storage(
        page=page or None,
        search=i.search or None,
        search_tags=i.search_tags and "on" or None,
        order=i.order or None,
        mode=("mode" in i) and i.mode or None,
    )

    pagination_data = []
    for n in util.pagination_numbers(page, total_num_of_pages):
        if n == 0 or n == page:
            page_link = ""
        else:
            page_link = links(linkstr, *(link_params + [nav_data]),
                                **dict(page=n))
        pagination_data.append(Storage(page_number=n, link=page_link))

    if len(pagination_data) < 2:
        pagination_data = []

    order_data = []
    for (n, o) in enumerate(orders):
        if (nav_data.order is None and n == 0) or nav_data.order == o:
            order_link = ""
        else:
            order_link = links(linkstr, *(link_params + [nav_data]),
                        **dict(order=o, page=None))
        order_data.append(Storage(
            order=o,
            order_name=_(o),
            link=order_link))

    mode_data = []
    for m in modes:
        if m == nav_data.mode:
            mode_link = ""
        else:
            mode_link = links(linkstr, *(link_params + [nav_data]),
                        **dict(mode=m))
        mode_data.append(Storage(
            mode=m,
            link=mode_link,
        ))

    return Storage(
        pagination_data=pagination_data,
        order_data=order_data,
        mode_data=mode_data,
        nav_data=nav_data,
        total_num_of_pages=total_num_of_pages,
        current_page=page or 1,
    )

###############################################################################
# FRONT PAGE
###############################################################################
class Index:

    def GET(self):
        i = web.input(page="1", order="", search="", search_tags="")
        page = int(i.page)

        topics = model.Projects()

        total_num_of_pages = topics.num_of_pages(length=config.topics_per_page)
        model.order_helper(topics, i.order)

        topics.limit_by_page(page, length=config.topics_per_page)
        topics.annotate_by_comments()
        topics.annotate_by_latest_points()  #!!!
        topics.annotate_by_profiles(default=DEFAULT_TOPIC_PROFILE)

        page_nav_data = page_nav_pack(i,
                  total_num_of_pages,
                  linkstr="index", orders=TOPIC_ORDERS)

        context = Storage(
            title = _("Front Page"),
            count_points = 1,
            count_views = 0,
        )

        context.update(page_nav_data)

        topics_highlighted = model.Projects(
            tags=model.Tags("official:highlighted"))
        topics_highlighted.annotate_by_profiles(default=DEFAULT_TOPIC_PROFILE)
        topics_highlighted.annotate_by_latest_points()
        topics_highlighted.annotate_by_comments()
        model.order_helper(topics_highlighted, config.main_page_highlighted_order)

        context.feeds = [
            Storage(type="application/atom+xml",
                url=feed_links.topics,
                title="Atom Feed of Topics")
            ]

        tags = model.tags_helper()

        get_page('index', context, topics, topics_highlighted, tags)

    def POST(self):
        """default login handler"""
        user = login_through()
        self.GET()
        return


###############################################################################
# ADVANCED SEARCH PAGE
###############################################################################
class Search:

    def GET(self):

        i = web.input(page="1", order="", search="", search_tags="", mode="list")
        page = int(i.page)

        user = get_user()

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

        page_nav_data = page_nav_pack(i,
                  total_num_of_pages,
                  linkstr="search", link_params=[],   #!!! ?
                  orders=POINT_ORDERS,
                  modes=["map", "list"],
                  )

        context = Storage(
            title=_("Advanced search: "),
            count_points=1,
            count_views=0,
            linktarget="",
            display_type=i.mode,
        )

        context.update(page_nav_data)

        context.feeds = [
            Storage(type="application/atom+xml",
                url=feed_links("search", search=i.search, 
                    search_tags=i.search_tags),
                title="Atom Feed of Search results")
            ]

        get_page('search', context, points)

###############################################################################
# USER PAGE
###############################################################################

class User:

    def GET(self, username):
        context = Storage(
            title=_("User: ") + username,
            count_points=1,
            count_views=0,
        )
        users = model.Users(username=username)
        if not users:
            redirect(1, _("No such user."), links.index)
            return

        users.annotate_by_projects()
        users.annotate_by_points()

        users.annotate_by_comments()
        user = users.first_item()

        user.points.annotate_by_comments()
        user.points.annotate_by_projects()

        user.projects.annotate_by_comments()

        user.points.annotate_by_tags()

        topics_subs = model.Projects(
            by_user_role=(user, "subscribed"))
        topics_subs.annotate_by_profiles(default=DEFAULT_TOPIC_PROFILE)
        topics_subs.annotate_by_points()
        topics_subs.annotate_by_comments()

        get_page('user', context, user, topics_subs)

###############################################################################
# USER SETTINGS PAGE
###############################################################################

# !!! this form should be also used in connection with signup
def user_settings_form(title):
    return form.Form( 
    form.Fieldset('fieldset', description=title),
    form.Password("oldpassword",
        description=_("Old password"),
#        post=<small>("Needed if you want to change password.")<small>,
    ), 
    form.Password("password",
        description=_("Password"),
    ), 
    form.Password("password2",
        description=_("Repeat password"),
    ), 
    form.Textbox("email",
        description=_("Email"),
    ), 
    form.Fieldset('end_of_fieldset'),
    )()

class User_settings:

    def GET(self, username):
        context = Storage(
            title=_("User: ") + username,
            count_points=1,
            count_views=0,
            form_action=links("user_settings", username)
        )
        users = model.Users(username=username)
        users.annotate_by_profiles(default=DEFAULT_USER_PROFILE)
        user = users.first_item()

        if not acl.authorize.view_user_settings(user):
            redirect(5, _("You do not have rights to access user information."), 
                links("user", username))
            return

        form = user_settings_form(_("Change settings"))
        form.fill(email=user.profile.email)

        get_page('user_settings', context, user, form)

    def POST(self, username):

        users = model.Users(username=username)
        user = users.first_item()

        if not acl.authorize.change_user_settings(user):
            redirect(5, _("You do not have rights to change user information."), 
                links("user", username))
            return

        form = user_settings_form(_("Change settings"))
        form.validates()

        not_forced_credentials_change = not acl.authorize.manage_users()

        if "oldpassword" not in form.d and not_forced_credentials_change:
            redirect(5, _("You do not have rights to change user information. Old password not given."), 
                links("user_settings", username))
            return

        password_change_required = "password" in form.d and "password2" in form.d and form.d.password and form.d.password2

        if password_change_required and form.d.password != form.d.password2:
            redirect(5, _("Password mismatch or empty password."), 
                links("user_settings", username))
            return

        if not_forced_credentials_change:
            # check old password
            a_credentials = Storage(username=username,
                                password=form.d.oldpassword)
            a_user = userbase.authenticate(a_credentials)
            if not a_user:
                redirect(5, _("You do not have rights to change user information."),  # old password wrong
                    links("user", username))
                return

        actions_messages = []

        if password_change_required:
            credentials = Storage(username=username,
                              password=form.d.password)

            password_is_bad, msg = userbase.bad_password(credentials.password)
            if password_is_bad:
                redirect(5, msg, 
                    links("user_settings", username))
                return

            try:
                userbase.change_credentials(user, credentials)
                actions_messages.append(_("Password changed."))
            except ValueError, x:
                actions_messages.append(_(x.message) + ".")
            

        profile = model.Profile(email=form.d.email)

        userbase.modify_user(user, profile)
        actions_messages.append(_("Profile updated."))

        redirect(2, " ".join(actions_messages),
                links("user", username))


class User_tools:

    def GET(self, username):
        context = Storage(
            title=_("User: ") + username,
            count_points=1,
            count_views=0,
            form_action=links("user_settings", username)
        )
        users = model.Users(username=username)
        users.annotate_by_profiles(default=DEFAULT_USER_PROFILE)
        user = users.first_item()

        if not acl.authorize.view_user_settings(user):
            redirect(5, _("You do not have rights to access user information."), 
                links("user", username))
            return

        get_page('user_tools', context, user, form)


class User_location:

    def GET(self, username, webinput=None):
        presets = webinput or web.input()
        presets.setdefault("geocoding", "")

        users = model.Users(username=username)
        users.annotate_by_profiles(default=DEFAULT_USER_PROFILE)
        user = users.first_item()

        if not acl.authorize.view_user_settings(user):
            redirect(5, _("You do not have rights to access user information."), 
                links("user", username))
            return


        session_info = session.session()
        
        lon = presets.get("lon", session_info.get("lon", ""))
        lat = presets.get("lat", session_info.get("lat", ""))
        c_zoom = session_info.get("zoom", config.topic_zoom)
        if lat and lon:
            c_lat, c_lon = lat, lon
        else:
            c_lat, c_lon = config.center_lat, config.center_lon

        util.defaultizer(presets, default=Storage(
            form_title=_("Set user location"),
            c_lat=c_lat,
            c_lon=c_lon,
            lat=lat,
            lon=lon,
            zoom=c_zoom
        ))
        if lat and lon:
            model.encode_coordinates(presets)
        else:
            presets.repr_lat = presets.repr_lon = ''

        params = Storage()  # params which survive address lookup
        params.op = "find"

        context = model.Storage(
            form_action = links("user_location", username),
            form_params = params,
        )

        set_map_context(context, (c_lat, c_lon), c_zoom, 
            has_new_point=True)

        get_page('user_location', context, user, presets)


    def POST(self, username, webinput=None):
        i = presets = webinput or web.input()

        user = login_through()
        if not user:
            return

        if not acl.authorize.change_user_settings(user):
            redirect(5, _("You do not have rights to access user information."), 
                links("user", username))
            return

        if i.get("op", None) is None:
            # how it can be???
            self.GET(username, webinput=webinput)
            return
        elif i.op == "find":
            # finding location by address
            i.update(model.geocoding_helper(i.get("address", ""), onfail=('', '')))
            self.GET(username, webinput=i)
            return
        elif i.op == "forget":
            session.remove_info(dict(lat=None, 
                                lon=None,
                                zoom=None))
            web.seeother(links("user", username))
            return
        elif i.op == "create":
            presets.address = ''  #???

            if not presets.lat:
                self.GET(username, webinput=i)
                return

            presets.repr_lat = float(presets.lat)
            presets.repr_lon = float(presets.lon)
            model.decode_coordinates(presets)

            # set location
            session.update_info(dict(lat=float(presets.lat), 
                                lon=float(presets.lon),
                                zoom=int(presets.zoom) - config.getmap_zoomshift))

            web.seeother(links("user", username))
            return


class Topic:

    def GET(self, topic_id):

        i = web.input(page="1", order="", search="", search_tags="", 
                mode=None)
        page = int(i.page)

        topics, topic = model.t_helper(topic_id)

        if not topics:
            redirect(5, _("No such topic. Delete from your bookmarks: ") + request_uri(), 
                links.index)
            return

        if i.mode is None:
            i.mode = topic.profile.default_view_mode
        if not i.order:
            i.order = topic.profile.default_view_order


        user = get_user()

        topics.annotate_by_datasources()
        topics.annotate_by_triggers()

        feeds = []    
        for feed in topic.datasources:
            if feed.type in ("autofeed", "autoissuefeed"):
                # update points
                feed_user = auto_author_user(feed.description.strip(), None)
                model.add_points_from_feed(topic, feed, feed_user)   #!!! user?!

        points = model.search_helper(i, topic=topic)

        total_num_of_pages = points.num_of_pages(length=config.points_per_page)

        tags = model.tags_helper(topic=topic)

        user_location = session.get_user_location()

        if user_location:
            points.annotate_by_distance(user_location.lat, user_location.lon)

        if i.mode != "map":  # map shows all points, not just one page
            model.order_helper(points, i.order)
            points.limit_by_page(page, length=config.points_per_page)

        points.annotate_by_comments()
        points.annotate_by_tags()
        points.annotate_by_profiles(default=DEFAULT_POINT_PROFILE)

        orders = POINT_ORDERS
        if not user_location:
            orders = list(orders)
            orders.remove("distance")

        page_nav_data = page_nav_pack(i,
                  total_num_of_pages,
                  linkstr="topic", link_params=[topic.id],
                  orders=orders,
                  modes=["map", "list"],
                  )

        context = Storage(
            title=_("Topic: ") + topic.title,
            count_points=1,
            count_views=0,
            linktarget="",
            display_type=i.mode,
            page_skin=topic.profile.topic_colour_scheme,
        )

        context.update(page_nav_data)

        if i.mode == "map":
            feed_link = feed_links("topic_points",
                topic.id, i, page=None)

            if "zoom" in topic.profile and \
                (topic.profile.zoom != "auto" or not points):
                c_lat, c_lon = topic.lat, topic.lon
                if topic.profile.zoom == "auto":
                    c_zoom = config.topic_zoom
                else:
                    c_zoom = topic.profile.zoom
            else:
                c_lat, c_lon, c_zoom = points.central_point(
                    config.center_lat, config.center_lon, config.topic_zoom)

            set_map_context(context, (c_lat, c_lon), c_zoom, 
                initial_feed=feed_link, topic=topic)

        #!!! should it use filtered point list?
        context.feeds = [
                Storage(type="application/atom+xml",
                    url=feed_links("topic_points", topic.id),
                    title="Atom Feed of Points"),
                ]

        get_page('topic', context, topic, points, tags)


class NewTopic:
    def GET(self):
        user = login_through(level="registered")
        if not user:
            return
        i = web.input()
        presets = Storage(i)

        util.defaultizer(presets, default=DEFAULT_TOPIC_PROFILE)

        topic_icons = config.topic_icons.split()
        topic_icons_data = []
        for ti in topic_icons:
            icon_url = links('default_topic_icons', ti)
            topic_icons_data.append(Storage(
                url=icon_url,
                name=ti,
                checked=(presets.topic_icon==icon_url),
            ))

        topic_colours = config.topic_colours.split()
        topic_colours_data = []
        for ti in topic_colours:
            topic_colours_data.append(Storage(
                name=ti,
                checked=(presets.topic_colour_scheme==ti),
            ))

        point_contributors = config.point_contributors.split(",")
        point_contributors_data = []
        for ti in point_contributors:
            point_contributors_data.append(Storage(
                name=ti,
                checked=(presets.point_contributors==ti),
            ))

        context = Storage(
            title=_("New Topic"),
            topic_icons_data=topic_icons_data,
            topic_colours_data=topic_colours_data,
            point_contributors_data=point_contributors_data,
        )

        get_page('new_topic', context, presets)

    def POST(self):
        user = login_through(level="registered")
        if not user:
            return

        i = web.input(topic_name=_("a topic"),
                      topic_description=_("No description"),
                      user_icon={},
                      )


        media_url = thumbnail_upload(i.user_icon, maxx=60, maxy=60)
        if media_url:
            topic_icon = config.base_url + media_url
        else:
            topic_icon = i.topic_icon

        topic = model.Projects.create(user=user,
            name=i.topic_name,
            lat=0.0, lon=0.0,
            url="",
            origin="",
            tags="",
            category="",
            description=i.topic_description,
        )

        profile = model.Profile(
            topic_icon=topic_icon,
        )

        util.defaultizer(profile, source=i, default=DEFAULT_TOPIC_PROFILE)

        model.set_object_property(topic, profile)

        #web.seeother(links("index"))
        web.seeother(links("topic_location", topic.id))
        return

class Point:
    def GET(self, topic_id, point_id):
        i = web.input(page="1", order="", search="", search_tags="")
        page = int(i.page)

        topics, topic, points, point = model.t_p_helper(topic_id, point_id)
        if not topics:
            redirect(5, _("No such topic. Delete from your bookmarks: ") + request_uri(), 
                links.index)
            return


        if not points:

            # deferred point creation hack
            user = get_user()
            deferred_topic_id, deferred_point_id = session.session().get("deferred_point", (None, None))
            if user and deferred_topic_id == topic.id and \
               deferred_point_id == int(point_id):
                model.enable_point_by_id(deferred_point_id, topic, user)
                session.remove_info({"deferred_point": None})
                redirect(1, _("Point created! "), 
                    links("point", topic.id, point_id))
                return
            # / deferred point creation 
            redirect(5, _("No such point. Delete from your bookmarks: ") + request_uri(), 
                links("topic", topic.id))
            return

        points.annotate_by_comments()

        comments = point.comments
        comments.annotate_by_profiles(default=DEFAULT_COMMENT_PROFILE)

        user = get_user()

        total_num_of_pages = comments.num_of_pages(length=config.comments_per_page)


        comments.limit_by_page(page, length=config.comments_per_page)

        page_nav_data = page_nav_pack(i,
                  total_num_of_pages,
                  linkstr="point", link_params=[topic.id, point.id],
                  orders=[])

        context = Storage(
            title=_("Point: ") + point.title,
            count_comments=1,
            count_views=0,
            linktarget="",
            map_context=Storage(
                zoom=int(config.point_map_zoom) + int(config.getmap_zoomshift), mapx=200, mapy=200),
            page_skin=topic.profile.topic_colour_scheme,
        )

        context.update(page_nav_data)

        related_topics = model.Projects(point=point)
        related_topics.annotate_by_profiles(default=DEFAULT_TOPIC_PROFILE)

        if 1:
            context.nearby_points = model.Points(
                nearby=(point.lat, point.lon, 
                        config.nearby_radius, None),
            )
        else:
            context.nearby_points = model.Points()

        context.nearby_points.filter_by_distance(point.lat, point.lon,
                max_distance=config.nearby_radius)
        context.nearby_points.sort_by_distance()
        context.nearby_points.limit_by(config.max_nearby_points)
        context.nearby_points.annotate_by_projects()
        for p in context.nearby_points:
            p.main_topic = p.projects.first_item()

        context.addcomment_form = point_addcomment_form(_("Comment"))

        context.feeds = [
                Storage(type="application/atom+xml",
                    url=feed_links("point_comments", topic.id, point.id),
                    title="Atom Feed of Comments")
                ]

        session_info = session.session()
        point_referer = session_info.get("point_referer", "")
        if point_referer:
            session.remove_info(dict(point_referer=None))
        context.point_referer = point_referer

        get_page('point', context, topic, point, comments, related_topics)


class Point_addtag:
    def GET(self, topic_id, point_id):
        i = web.input(tags="")

        topics, topic, points, point = \
            model.t_p_helper(topic_id, point_id)

        user = login_through()
        if not user:
            return

        new_tags = model.Tags(i.tags)
        new_tags.tag_point(point, user)

        web.seeother(links('point', topic.id, point.id))

class Point_delete:
    def GET(self, topic_id, point_id):
        topics, topic, points, point = \
            model.t_p_helper(topic_id, point_id)

        user = login_through()
        if not user:
            return

        if acl.authorize.delete_point(topic, point):
            points.hide()

        web.seeother(links('topic', topic.id))

class Datasource_delete:
    def GET(self, topic_id, ds_id):
        topics, topic, dss, ds = \
            model.t_d_helper(topic_id, ds_id)

        user = login_through()
        if not user:
            return

        if acl.authorize.manage_topic(topic):
            dss.delete(from_project=topic)

        web.seeother(links('topic', topic.id))

class Topic_delete:
    def GET(self, topic_id):
        topics, topic = \
            model.t_helper(topic_id)

        user = login_through()
        if not user:
            return

        if acl.authorize.delete_topic(topic):
            topics.hide()

        web.seeother(links('index'))

def point_addcomment_form(title):
    return form.Form( 
    form.Fieldset('fieldset', description=title),
    form.Editor("text",
        form.required_wide,
        description=_("Comment text"),
        cols=50, rows=4,
    ), 
    form.File("file",
        description=_("Picture"),
    ), 
#    form.Textbox("url",
#        description=_("Related website URL"),
#    ), 
#    form.Textbox("url_description",
#        description=_("Related website description"),
#    ), 
    form.Fieldset('end_of_fieldset'),
    )()



class Point_addcomment:
    def POST(self, topic_id, point_id):
        i = web.input(file={})

        topics, topic, points, point = \
            model.t_p_helper(topic_id, point_id)

        user = login_through()
        if not user:
            return

        res = model.store_attachment(point.id, user,
                attach_type="any",
                origin='',
                commenttext=i.text, 
#                url=i.url, 
#                url_title=i.url_description, 
                fileinfo=i.file)
        web.seeother(links('point', topic.id, point.id))


class Point_editcomment:
    def GET(self, topic_id, point_id, comment_id):

        user = login_through()
        if not user:
            return


        topics, topic, points, point, comments, comment = \
            model.t_p_c_helper(topic_id, point_id, comment_id)

        if not acl.authorize.edit_comment(topic, point, comment):
            redirect(5, _("You do not have rights to edit the comment."), 
                links("point", topic.id, point.id))
            return

        i = web.input(file={})

        # check that it belongs to point!!!

        context = Storage(
            title = _("Edit comment"),
            page_skin=topic.profile.topic_colour_scheme,
        )
        context.addcomment_form = point_addcomment_form(_("Comment"))
        context.addcomment_form.fill(
            text=comment.text,
            )  #!!!

        get_page('point_editcomment', context, topic, point, comment)

    def POST(self, topic_id, point_id, comment_id):

        user = login_through()
        if not user:
            return

        topics, topic, points, point, comments, comment = \
            model.t_p_c_helper(topic_id, point_id, comment_id)

        if not acl.authorize.edit_comment(topic, point, comment):
            redirect(5, _("You do not have rights to edit the comment."), 
                links("point", topic.id, point.id))
            return

        i = web.input(file={})

        res = model.store_attachment(point.id, user,
                attach_type="any",
                origin='',
                commenttext=i.text, 
#                url=i.url, 
#                url_title=i.url_description, 
                fileinfo=i.file,
                comment=comment)

        web.seeother(links('point_editcomment', topic.id, point.id, comment.id))


class Point_deletecomment:
    def GET(self, topic_id, point_id, comment_id):

        user = login_through()
        if not user:
            return

        topics, topic, points, point, comments, comment = \
            model.t_p_c_helper(topic_id, point_id, comment_id)

        if not acl.authorize.delete_comment(topic, point, comment):
            redirect(5, _("You do not have rights to delete the comment."), 
                links("point", topic.id, point.id))
            return

        if acl.authorize.delete_comment(topic, point, comment):
            comments.hide()

        web.seeother(links('point', topic.id, point.id))


class Point_settings:
    def GET(self, topic_id, point_id, webinput=None):
        presets = webinput or web.input()
        presets.setdefault("geocoding", "")

        topics, topic, points, point = \
            model.t_p_helper(topic_id, point_id)

        user = login_through()
        if not user:
            return

        # special tags filtered out
        if not acl.authorize.manage_special_tags():
            point.tags.filter_not_in_namespaces(["special"])

        util.defaultizer(presets, default=Storage(
            form_title=_("Edit point settings"),
            tags_example=_('dangerous ugly disturbing question complaint'),
            title_example=_('Dangerous concrete blocks'),
            fixed_tags = "",
            menu_tags = [],
            c_lat=point.lat or config.center_lat,
            c_lon=point.lon or config.center_lon,
            lon=point.lon or "",
            lat=point.lat or "",
            name=point.title,
            tags=point.tags.for_str(),
            description=point.comments.first_item().text,
        ))
        if not presets.lat:
            presets.repr_lat, presets.repr_lon = '', ''
        else:
            model.encode_coordinates(presets)


        params = Storage()  # params which survive address lookup
        util.defaultizer(params, source=presets, 
            default={"fixed_tags": '', "name": '', "tags": '', 
                "description": '', "url": '', "referer": '',})
        params.op = "find"

        context = model.Storage(
            form_action = links("point_settings", topic.id, point.id),
            form_params = params,
            page_skin=topic.profile.topic_colour_scheme,
        )

        set_map_context(context, (presets.c_lat, presets.c_lon), config.topic_zoom, 
            has_new_point=True, topic=topic)

        get_page('point_settings', context, topic, point, presets)

    def POST(self, topic_id, point_id):
        topics, topic, points, point = \
            model.t_p_helper(topic_id, point_id)

        presets = i = web.input(file={})

        user = login_through()
        if not user:
            return

        if i.get("op", None) is None:
            # how it can be???
            self.GET(topic_id, point_id)
            return
        elif i.op == "find":
            # finding location by address
            i.update(model.geocoding_helper(i.get("address", ""), onfail=('', '')))
            self.GET(topic_id, point_id, webinput=i)
            return
        elif i.op == "create":
            #
            presets.origin = ''
            presets.address = ''  #???
            presets.setdefault('url', '')
            tags = model.Tags(presets.tags)

            if presets.lat:
                presets.repr_lat = float(presets.lat)
                presets.repr_lon = float(presets.lon)
                model.decode_coordinates(presets)

                point.lat = float(presets.lat)
                point.lon = float(presets.lon)

            point.title = presets.name

            point_description = point.first
            point_description.text = presets.description

            # updating settings
            model.Points.update(user, point, 
                point_description, tags,
                fileinfo=i.file,
                guard_special_tags=not acl.authorize.manage_special_tags(),
            )

            web.seeother(links("point", topic.id, point.id))
            return


class Topic_location:
    def GET(self, topic_id, webinput=None):
        presets = webinput or web.input()
        presets.setdefault("geocoding", "")

        topics, topic = model.t_helper(topic_id)
        topics.annotate_by_points()

        user = login_through()
        if not user:
            return

        if not acl.authorize.manage_topic(topic):
            redirect(5, _("You do not have rights for that."), 
                links("topic", topic.id))
            return

        lat = presets.get("lat", topic.lat) or ""
        lon = presets.get("lon", topic.lon) or ""

        if "zoom" in topic.profile and topic.profile.zoom != "auto":
            c_zoom = topic.profile.zoom
            autozoom = "0"
        else:
            c_lat, c_lon, c_zoom = topic.points.central_point(
                config.center_lat, config.center_lon, config.topic_zoom)
            if "zoom" in topic.profile and topic.profile.zoom == "auto":
                autozoom = "1"
            else:
                autozoom = "0"

        c_lat = lat or config.center_lat
        c_lon = lon or config.center_lon

        util.defaultizer(presets, default=Storage(
            form_title=_("Set topic map"),
            c_lat=c_lat,
            c_lon=c_lon,
            lat=lat,
            lon=lon,
            repr_lat="",
            repr_lon="",
            zoom=c_zoom,
            autozoom=autozoom,
        ))

        params = Storage()  # params which survive address lookup
        params.autozoom = autozoom
        params.op = "find"

        context = model.Storage(
            form_action = links("topic_location", topic.id),
            form_params = params,
            page_skin=topic.profile.topic_colour_scheme,
        )

        set_map_context(context, (presets.c_lat, presets.c_lon), presets.zoom, 
            has_new_point=True, topic=topic)

        presets.zoom = str(int(presets.zoom) + config.getmap_zoomshift)

        get_page('topic_location', context, topic, presets)

    def POST(self, topic_id, webinput=None):
        i = presets = webinput or web.input()

        topics, topic = model.t_helper(topic_id)

        user = login_through()
        if not user:
            return

        if not acl.authorize.manage_topic(topic):
            redirect(5, _("You do not have rights for that."), 
                links("topic", topic.id))
            return

        if i.get("op", None) is None:
            # how it can be???
            self.GET(topic_id, webinput=webinput)
            return
        elif i.op == "find":
            # finding location by address
            i.update(model.geocoding_helper(i.get("address", ""), onfail=('', '')))
            self.GET(topic_id, webinput=i)
            return
        elif i.op == "create":
            presets.address = ''  #???

            if not presets.lat:
                self.GET(topic_id, webinput=i)
                return

            presets.repr_lat = float(presets.lat)
            presets.repr_lon = float(presets.lon)
            model.decode_coordinates(presets)

            topic.lat = float(presets.lat)
            topic.lon = float(presets.lon)

            profile = model.Profile()
            if presets.autozoom == "0":
                profile.zoom = str(int(presets.zoom) - config.getmap_zoomshift)
            else:
                profile.zoom = "auto"

            model.set_object_property(topic, profile)

            # updating settings
            model.Projects.update(user, topic)

            web.seeother(links("topic", topic.id))
            return


class Topic_addwidget:
    def POST(self, topic_id):
        i = web.input(file={})

        if "id" in i and i.id:
            # existing widget
            topics, topic, comments, comment = model.t_c_helper(topic_id, i.id)
        else:
            topics, topic = model.t_helper(topic_id)

        user = login_through()
        if not user:
            return

        if not acl.authorize.manage_topic(topic):
            redirect(5, _("You do not have rights for that."), 
                links("topic", topic.id))
            return

        if "id" in i and i.id:
            res = model.store_attachment(topic.id, user,
                attach_type="widget",
                origin='',
                commenttext=i.widget_code, 
                fileinfo=i.file,
                comment=comment)
        else:
            res = model.store_attachment(topic.id, user,
                attach_type="widget",
                origin='',
                commenttext=i.widget_code, 
                fileinfo=i.file)
        web.seeother(links('topic', topic.id))

########### NEW POINT #########################################################

class Topic_newpoint:
    def GET(self, topic_id, webinput=None):
        topics, topic = model.t_helper(topic_id)

        presets = i = webinput or web.input()
        presets.setdefault("geocoding", "")
        if "title" in presets and not "from_widget" in presets:
            presets.name = presets.title
            del presets.title

        if "description_hidden" in presets:
            presets.description = presets.description_hidden
            del presets.description_hidden

        # point template used
        if "template" in presets and presets.template:
            points = model.Points(id=int(presets.template))
            if points:
                point = points.first_item()
                points.annotate_by_comments()
                points.annotate_by_tags()
                presets.c_lat = str(point.lat)
                presets.c_lon = str(point.lon)
                presets.title_example = point.title
                presets.tags = point.tags.for_str()   #???
                presets.tags_example = point.tags.for_str()   #???
                presets.description = point.first.text
                
            del presets.template

        # post to UM from Google maps
        if "lat" not in presets and "url" in presets:
            if "maps.google.com" in presets.url and "ll" in presets.url:
                try:
                    presets.lat, presets.lon = \
                        map(float, util.parse_qs(presets.url)["ll"][0].split(","))
                    presets.geocoding = "successful"
                    model.encode_coordinates(presets)
                except:
                    pass
            elif "en.wikipedia.org" in presets.url:
                # wikipedia
                # !!! put somewhere else?
                presets.name = web.rstrips(presets.name, " - Wikipedia, the free encyclopedia")
                if not "description" in presets:
                    presets.description = '<a href="%s">%s</a>' % (presets.url, "Wikipedia")

                place = presets.url.split("/")[-1]
                try:
                    fc = urllib.urlopen("http://en.wikipedia.org/w/query.php?what=content&format=xml&titles=" + place).read()
                    wiki_re = re.compile(r"""{{coor.+ ?(dms?)([|0-9ENWS]+)""")
                    m = wiki_re.search(fc)
                except:
                    m = None
                if m:
                    fmt, data = m.groups()
                    lat = lon = ""
                    if fmt.lower() == "dm":
                        data = data.split("|")
                        lat_e = data[1:4]
                        lon_e = data[4:7]
                        lat = float(lat_e[0]) + float(lat_e[1]) / 60
                        lon = float(lon_e[0]) + float(lon_e[1]) / 60
                        if lat_e[-1].lower() == "S":
                            lat = -lat
                        if lon_e[-1].lower() == "W":
                            lon = -lon
                    elif fmt.lower() == "dms":
                        data = data.split("|")
                        lat_e = data[1:5]
                        lon_e = data[5:9]
                        lat = float(lat_e[0]) + float(lat_e[1]) / 60 + float(lat_e[2]) / 3600
                        lon = float(lon_e[0]) + float(lon_e[1]) / 60 + float(lon_e[2]) / 3600
                        if lat_e[-1].lower() == "S":
                            lat = -lat
                        if lon_e[-1].lower() == "W":
                            lon = -lon
                    if lat != "":
                        presets.lat, presets.lon = lat, lon
                        presets.geocoding = "successful"
                        model.encode_coordinates(presets)

        if presets.geocoding == "successful":
            presets.c_lat = lat = presets.lat
            presets.c_lon = lon = presets.lon
        elif presets.get("repr_lat", ""):
            presets.repr_lat = float(presets.repr_lat)
            presets.repr_lon = float(presets.repr_lon)
            model.decode_coordinates(presets)
            lat = presets.lat
            lon = presets.lon
        else:
            lat = presets.get("lat", "")
            lon = presets.get("lon", "")

        # Logic for zoom, lat, lon
        c_lat = presets.get("c_lat", lat)
        c_lon = presets.get("c_lon", lon)
        if "zoom" in presets and presets.zoom != "auto":
            c_zoom = int(presets.zoom)
        else:
            if "zoom" in topic.profile and topic.profile.zoom != "auto":
                c_zoom = int(topic.profile.zoom)
            else:
                c_zoom = config.topic_zoom
        if not c_lon:
            if "zoom" in topic.profile:
                c_lat, c_lon = topic.lat, topic.lon
            else:
                c_lat, c_lon = config.center_lat, config.center_lon

        c_lat = float(c_lat)
        c_lon = float(c_lon)

        util.defaultizer(presets, default=Storage(
            form_title="",
            tags_example=_('dangerous ugly disturbing question complaint'),
            title_example=_('Dangerous concrete blocks'),
            c_lat=c_lat,
            c_lon=c_lon,
            lon=lon,
            lat=lat,
            repr_lon="",
            repr_lat="",
            c_zoom=c_zoom,
        ))
        # !!!
        params = Storage()  # params which survive address lookup
        util.defaultizer(params, source=presets, 
            default={"fixed_tags": '', "name": '', "tags": '', 
                "title_example": '', "tags_example": '',
                "tags_for_menu": '',
                "description": '', "url": '', "referer": '',})
        params.op = "find"

        presets.menu_tags = model.Tags(params.tags_for_menu)

        context = Storage(
            title = _("Add Point"),
            count_comments = 1,
            count_views = 0,
            linktarget="",
            form_action=links("topic_newpoint", topic.id),
            form_params=params,
            page_skin=topic.profile.topic_colour_scheme,
        )

        set_map_context(context, (c_lat, c_lon), c_zoom, 
            has_new_point=True, topic=topic)

        get_page('new_point', context, topic, presets)

    def POST(self, topic_id):
        topics, topic = model.t_helper(topic_id)

        presets = i = web.input(file={})

        # this is security loophole: topic owner
        # can allow contribution without checking captcha
        if acl.authorize.add_point(topic):  # no login needed
            user = get_user()
            if user is None:
                user = auto_anonymous_user()
            deferred = False
        else:
            deferred = True
            user = auto_anonymous_user()

        if i.get("op", None) is None:
            # how it can be???
            self.GET(topic_id)
            return
        elif i.op == "find":
            if "description_hidden" in presets:
                presets.description = presets.description_hidden
                del presets.description_hidden
            # finding location by address
            i.update(model.geocoding_helper(i.get("address", ""), onfail=('', '')))
            self.GET(topic_id, webinput=i)
            return
        elif i.op == "create":
            #
            presets.origin = ''
            presets.address = ''  #???
            presets.setdefault('url', '')
            fixed_tags = presets.get("fixed_tags", "")
            tag_from_menu = presets.get("tag_from_menu", "")
            tags = presets.tags + (fixed_tags and (" " + fixed_tags) or "") \
                     + (tag_from_menu and (" " + tag_from_menu) or "")

            if not presets.lat:
                self.GET(topic_id, webinput=i)
                return

            session.update_info(dict(point_referer=presets.get("referer", "")))

            presets.repr_lat = float(presets.lat)
            presets.repr_lon = float(presets.lon)
            model.decode_coordinates(presets)

            if not presets.name:
                presets.name = util.first_line(util.unescape_refs(presets.description), 40)
            # !!! problem with &auml;

            if not presets.name:
                presets.name = "-"

            point = model.Points.create(
                user=user,
                name=presets.name or "-",
                lat=presets.lat,
                lon=presets.lon,
                url=presets.url,
                origin=presets.origin,
                tags=tags,
                description=presets.description or " ",
                address=presets.address,
                project_id=topic.id,
                deferred=deferred,  # create invisible
                fileinfo=i.file,
            )

            if not deferred:
                web.seeother(links("point", topic.id, point.id))
            else:
                # !!! what if it is 2nd deferred point? delete previous?
                session.update_info({'deferred_point': (topic.id, point.id)})
                link = links("point", topic.id, point.id)
                if topic.profile.point_contributors in ("visitors", "anyone"):
                    user = login_through(came_from=link, post_login=True)
                else:
                    user = login_through(level="registered", came_from=link, post_login=True)
            return

class Topic_tools:
    def GET(self, topic_id):
        topics, topic = model.t_helper(topic_id)
        topics.annotate_by_datasources()
        topics.annotate_by_triggers()

        context = Storage(
            title = _("Topic tools"),
            page_skin=topic.profile.topic_colour_scheme,
        )
        get_page('topic_tools', context, topic)


class Topic_widgets:
    def GET(self, topic_id):
        topics, topic = model.t_helper(topic_id)

        context = Storage(
            title = _("Topic widgets"),
            page_skin=topic.profile.topic_colour_scheme,
        )
        get_page('topic_widgets', context, topic)


def topic_subscription_form():
    return form.Form( 
    form.Fieldset('fieldset', description=_("Subscription")),
    form.Checkbox("subscribed",
        description=_("Active"),
    ), 
    form.Fieldset('end_of_fieldset'),
    )()

class Topic_subscription:
    def GET(self, topic_id):
        user = login_through()
        if not user:
            return
        topics, topic = model.t_helper(topic_id)
        topics.annotate_by_datasources()

        context = Storage(
            title = _("Topic subscription"),
            page_skin=topic.profile.topic_colour_scheme,
        )

        subscription_status = "subscribed" in model.Points.get_roles(topic, user)
        form = topic_subscription_form()
        form.fill(subscribed=subscription_status)

        get_page('topic_subscription', context, topic, form)

    def POST(self, topic_id):
        user = login_through()
        if not user:
            return
        topics, topic = model.t_helper(topic_id)
        topics.annotate_by_datasources()

        form = topic_subscription_form()

        if not form.validates():
            return  #!!! should not happen

        if form.d.subscribed:  # subscribe
            model.Points.set_roles(topic, user, ["subscribed"], user)
        else:  # unsubscribe
            model.Points.unset_roles(topic, user, ["subscribed"], user)

        web.seeother(links("topic", topic.id))

class Topic_settings:
    def GET(self, topic_id):
        user = login_through()
        if not user:
            return
        topics, topic = model.t_helper(topic_id)
        topics.annotate_by_comments()

        topic_description = topic.first.text

        presets = Storage(
            topic_name=topic.title,
            topic_description=topic_description,
        )

        util.defaultizer(presets, source=topic.profile, 
                        default=DEFAULT_TOPIC_PROFILE)

        topic_icons = config.topic_icons.split()
        topic_icons_data = []
        for ti in topic_icons:
            icon_url = links('default_topic_icons', ti)
            checked = presets.topic_icon==icon_url
            topic_icons_data.append(Storage(
                url=icon_url,
                name=ti,
                checked=checked,
            ))
        # do we have custom icon?
        if "/media?" in presets.topic_icon:
            topic_icons_data.append(Storage(
                url=presets.topic_icon,
                name="custom",
                checked=True,
            ))

        topic_colours = config.topic_colours.split()
        topic_colours_data = []
        for ti in topic_colours:
            topic_colours_data.append(Storage(
                name=ti,
                checked=(presets.topic_colour_scheme==ti),
            ))

        context = Storage(
            title = _("Topic settings"),
            topic_icons_data=topic_icons_data,
            topic_colours_data=topic_colours_data,
            page_skin=topic.profile.topic_colour_scheme,
        )
        get_page('topic_settings', context, topic, presets)

    def POST(self, topic_id):
        user = login_through()
        if not user:
            return

        i = web.input(user_icon={})

        topics, topic = model.t_helper(topic_id)
        topics.annotate_by_comments()

        topic_description = topic.first
        topic_description.text = i.topic_description
        topic_description.type = 'comment'

        topic.title = i.topic_name

        model.Projects.update(user, topic)
        model.Comments.update(topic_description, topic, user)

        profile = model.Profile()
        util.defaultizer(profile, source=i, 
                        default=DEFAULT_TOPIC_BASIC_PROFILE)

        # new icon upload?
        media_url = thumbnail_upload(i.user_icon, maxx=60, maxy=60)
        if media_url:
            topic_icon = config.base_url + media_url
        else:
            topic_icon = profile.topic_icon

        if topic_icon != "custom":
            profile.topic_icon = topic_icon

        model.set_object_property(topic, profile)
        web.seeother(links("topic", topic.id))


class Topic_feedback:
    def GET(self, topic_id):
        user = login_through()
        if not user:
            return
        topics, topic = model.t_helper(topic_id)
        topics.annotate_by_comments()

        set_config_item(None, 'feedback_topic_id', topic.id)
        config.feedback_topic_id = topic.id

        web.seeother(links('topic', topic_id))


def topic_advanced_form():
    if acl.authorize.change_um_settings():
        admin_extras = [
            form.Fieldset('fieldset', description=_("Administrator's extras")),
            form.Textbox("origin",
                description=_("Topic origin"),
#<small>$("Empty for most cases. May be: official")</small>
            ),

            form.Textbox("tags",
                description=_("Topic tags"),
#<small>$("Empty for most cases. May be: official:highlighted, official:geocoding_source")</small>
            ),

            form.Dropdown("topic_owner_rights",
                [("topic_only", _("Topic only")), ("topic_and_points", _("Topics and points"))],
                description=_("Topic owners management rights"),
                size=1,
#<small>$("Empty for most cases. May be: official")</small>
            ),

            form.Textbox("getmap_layers", description=_("getmap_layers"),),
            form.Textbox("getmap_layers1", description=_("getmap_layers1"),),
            form.Textbox("getmap_layers2", description=_("getmap_layers2"),),
            form.Textbox("getmap_zoom1", description=_("getmap_zoom1"),),
            form.Textbox("getmap_zoom2", description=_("getmap_zoom2"),),
            form.Textbox("getmap_zoomshift", description=_("getmap_zoomshift"),),
            form.Textarea("getmap_params", description=_("getmap_params"),),
            form.Textarea("getmap_custom_init", description=_("getmap_custom_init"), cols=50, rows=10),

            form.Fieldset('end_of_fieldset'),
        ]
    else:
        admin_extras = []

    return form.Form(*[
    form.Fieldset('fieldset', description=_("Settings")),
    form.Textbox("topic_page_elements",
        description=_("Topic page elements"),
#<small>("Elements to show on the topic page. Example: tagcloud,new point button,widgets,search,about")</small>
    ), 
    form.Textbox("topic_point_page_contents",
        description=_("Point page content"),
#<small>("Elements to show on the point page content block. Example: title,description,author,tags,addtag,comments")</small>
    ), 
    form.Textbox("topic_point_comments_elements",
        description=_("Point page comment section elements"),
#<small>("Elements to show on the point page comments section. Example: comments,pagination,addcomment,feed")</small>
    ), 
    form.Textbox("point_list_show",
        description=_("Point information display on point list"),
#<small>$("Fields to show in the point list.") Example: title,added,url,description-full,description-abbr,author,tags,distance</small>
    ),

    form.Dropdown("default_view_mode",
        [("list", _("list")), ("map", _("map"))],
        description=_("Default view mode"),
        size=1,
#<small>$("Choose default mode to the topic view") Example: list, map</small>
    ),

    form.Dropdown("default_view_order",
        [(o, _(o)) for o in config.main_page_point_orders],
        description=_("Default view order for point list"),
        size=1,
#<small>$("Choose default order for the topic view poit list (newest, oldest, etc)")</small>
    ),

    form.Dropdown("point_contributors",
        [(o, _(o)) for o in config.point_contributors.split(",")],
        description=_("Who can add points"),
        size=1,
#<small>$("Minimal rights to create the point")</small>
    ),

    form.Fieldset('end_of_fieldset'),
    ] + admin_extras
    )()


class Topic_advanced:
    """Advanced settings for the topic
    """

    def GET(self, topic_id): 
        user = login_through()
        if not user:
            return

        topics, topic = model.t_helper(topic_id)

        webinput = web.input()

        context = Storage(
            title=_("Advanced topic settings"),
            action_link="",
            page_skin=topic.profile.topic_colour_scheme,
        )

        presets = Storage(origin=topic.origin, tags=topic.tags.for_str())
        util.defaultizer(presets, source=topic.profile, 
                        default=DEFAULT_TOPIC_PROFILE)

        form = topic_advanced_form()

        if 'topic_page_elements' not in webinput or not form.validates():
#            print form.validates(), topic.profile.keys()
            form.fill(**presets)   #!!!?
            get_page("topic_advanced", context, topic, form)
        else:
            profile = model.Profile()
            util.defaultizer(profile, source=webinput, 
                            default=DEFAULT_TOPIC_ADVANCED_PROFILE)

            if acl.authorize.change_um_settings():
                topic.origin = webinput.origin.strip().lower()
                if topic.origin not in ("", "official"):  #!!!
                    topic.origin = ''
                tags = model.Tags(webinput.tags)
                # updating settings
                model.Projects.update(user, topic, tags=tags)
            else:
                model.Projects.update(user, topic)
                del profile.topic_owner_rights

            model.set_object_property(topic, profile)
            web.seeother(links("topic", topic.id))


    POST = GET


class SetLanguage:

    def GET(self):
        i = web.input(lang="en")
        i18n.set_language_cookie(i.lang)
        try:
            web.seeother(web.ctx.environ["HTTP_REFERER"])
        except:
            web.seeother(links.index)


class Doc:
    def GET(self, doc_name):
        context = Storage()
        own_content = model.doc_helper(context, doc_name, i18n.getLanguage())
        get_page('doc', context, own_content)

class StaticDoc:
    def GET(self, doc_name):
        context = Storage()
        get_page('staticdoc', context, getattr(view.docs, doc_name))

class Guide:
    def GET(self, doc_name):
        context = Storage()
        try:
            print render.guide(context, getattr(view.docs, doc_name))
        except:
            print render.guide(context, getattr(view.docs, "help"))

class GuideObject:
    def GET(self, doc_name):
        web.seeother(links("static") + "docs_img/" + doc_name)

class Feedback:
    def GET(self):
        web.seeother(links("topic", config.feedback_topic_id))

class Turing:
    def GET(self, file_key):
        try:
            print turing.download_captcha(file_key)
        except:
            print "no"

class Media:
    def GET(self):
        form = web.input(file_key=None, preview=0)
        if not form.file_key:
            print _("Not found")
        else:
            if not int(form.preview):
                print media.downloadMediaFile(form.file_key)
            else:
                print media.downloadPreview(form.file_key)


class Login:
    def POST(self):
        i = web.input()
        came_from = i.get("came_from",
            web.ctx.environ.get("HTTP_REFERER", links.index))
        user = login_through(came_from=came_from, 
                            post_login=True)
        if not user:
            return
        if user.username:
            web.seeother(came_from)
            return

    GET = POST

class Logout:
    def GET(self):
        unbind_user()
        print render.logout(None, url=links.index)

class MapSearch:
    def GET(self):
        context = Storage()
        set_map_context(context, 
            (config.center_lat, config.center_lon), config.zoom)  #!!!

        print render.map_search(context)


class Skindemo:
    def GET(self):
        i = web.input(scheme_name="A")
        css_url = links("page_skin", i.scheme_name[0])   #!!! make more secure
        print render.skindemo(None, css_url=css_url, scheme_name=i.scheme_name[0])


class GetMapFast:

    def GET(self):
        getmap_server = config.getmap_server
        if getmap_server:
            url = getmap_server + web.ctx.environ["QUERY_STRING"]

            headers, fh = url_handler.loadURLFast(url, cache_dir="MAP_CACHE/", 
                            aged=config.getmap_tile_aged_in_cache)
            try:
                web.header("content-type", headers["content-type"])
            except:
                pass
            print fh.read()


class Signup:
    def GET(self):
        user = get_user()
        captcha_key = turing.new_captcha()
        presets = web.input()
        context = Storage(
            title = _("Sign up"),
            captcha_url=config.base_url + "/turing/" + captcha_key,
            captcha_key=captcha_key,
            method="POST",
            form_action=links.signup,
        )
        get_page("signup", context, params=presets)

    def POST(self):
        i = web.input(came_from=links.base_url)
        user_word = i.get("user_word", "")
        captcha_key = i.get("captcha_key", "CAPTCHAS/no")

        captcha_test = turing.check_captcha(captcha_key, user_word)
        if captcha_test:
            redirect(5, _("Visual code is wrong."), 
                links("signup", came_from=links.base_url))
            return

        if i.password != i.password2:
            redirect(5, _("Passwords do not match."), 
                links("signup", came_from=i.came_from))
            return

        credentials = Storage(username=i.username, password=i.password)

        username_is_bad, msg = userbase.bad_username(credentials.username)
        if username_is_bad:
            redirect(5, _(msg), 
                links("signup", came_from=i.came_from))
            return

        password_is_bad, msg = userbase.bad_password(credentials.password)
        if password_is_bad:
            redirect(5, _(msg), 
                links("signup", came_from=i.came_from))
            return

        group = model.Groups("users").first_item()

        profile = None
        if i.get("email", None) and "@" in i.email:
            profile = Storage(email=i.email.strip().lower(),)

        user = userbase.add_user(credentials, profile, group=group)
        if user is None:
            redirect(5, _("Error occured. User not added."), 
                links("signup", came_from=i.came_from))
            return

        redirect(3, _("User created."), 
            links("login", username=user.username, came_from=i.came_from))


def add_topic_user_form():
    return form.Form( 
    form.Fieldset('fieldset', description=_("Add user role in this topic")),
    form.Textbox("username",
        form.required,
        form.Validator(_('Must be filled'), lambda x:x.strip()),
        description=_("Username of a registered user"),
    ), 
    form.Checkbox("topic_manager",
        description=_("Manager?"),
    ), 
    form.Checkbox("topic_user_manager",
        description=_("User manager?"),
    ), 
    form.Checkbox("topic_subscriber",
        description=_("Subscriber?"),
    ), 
    form.Fieldset('end_of_fieldset'),
    )()

class Topic_adminlist:
    def GET(self, topic_id): 
        user = login_through()
        if not user:
            return

        topics, topic = model.t_helper(topic_id)

        if not acl.authorize.manage_topic_admins(topic):
            redirect(5, _("You do not have rights for that."), 
                links("topic", topic.id))
            return

        topics.annotate_by_users()

        context = Storage(
            title=_("List of administrators for ") + topic.title,
            page_skin=topic.profile.topic_colour_scheme,
        )

        # annotate users with roles in this topic
        for u in topic.users:
            trans = [_("label_" + ur) 
                     for ur in model.Points.get_roles(topic, u)]
            u.roles = ", ".join(trans)

        form = add_topic_user_form()

        get_page("topic_adminlist", context, topic, form)


    def POST(self, topic_id): 
        user = login_through()
        if not user:
            return

        topics, topic = model.t_helper(topic_id)

        if not acl.authorize.manage_topic_admins(topic):
            redirect(5, _("You do not have rights for that."), 
                links("topic", topic.id))
            return

        topics.annotate_by_users()

        # annotate users with roles in this topic
        for u in topic.users:
            trans = [_("label_" + ur) 
                     for ur in model.Points.get_roles(topic, u)]
            u.roles = ", ".join(trans)

        form = add_topic_user_form()

        context = Storage(title=_("List of administrators for ") + topic.title)

        if not form.validates():
            get_page("topic_adminlist", context, topic, form)
            return

        i = web.input()

        var_to_role = dict(
            topic_manager="manage_project",
            topic_user_manager="manage_users",
            topic_subscriber="subscribed"
        )

        roles = []
        managed_users = model.Users(username=i.username)

        if not managed_users:
            get_page("topic_adminlist", context, topic, form)
            redirect(5, _("Failure: no such user " + i.username), 
                links("topic_adminlist", topic.id))

        managed_user = managed_users.first_item()

        for v in var_to_role:
            if i.get(v, ""):
                roles.append(var_to_role[v])

        # clear the table first
        all_roles = var_to_role.values()
        result, diag = model.Projects.unset_roles(
                            topic, managed_user, all_roles, user)
        # then add
        result, diag = model.Projects.set_roles(
                            topic, managed_user, roles, user)

        if result:
            get_page("topic_adminlist", context, topic, form)
            redirect(1, _("User managed successfully."), 
                links("topic_adminlist", topic.id))
        else:
            get_page("topic_adminlist", context, topic, form)
            redirect(5, _("Failure: " + diag), 
                links("topic_adminlist", topic.id))

        


############# Import points from feed  ###############################

def feed_import_form():
    return form.Form( 
    form.Fieldset('fieldset', description=_("Enter feed for importing")),
    form.Textbox("url",
        form.required,
        form.Validator(_('Must be filled'), lambda x:x.strip()),
        description=_("Feed address (URL)"),
    ), 
    form.Textbox("description",
        description=_("Describe the feed"),
    ), 
    form.Checkbox("issues",
        description=_("Feed for issues?"),
    ), 
    form.Textbox("freq",
        description=_("Check interval in seconds"),
    ), 
    form.Fieldset('end_of_fieldset'),
    )()


class FeedImport:
    def GET(self, topic_id): 
        user = login_through()
        if not user:
            return

        topics, topic = model.t_helper(topic_id)
        context = Storage(
            title=_("New feed for ") + topic.title,
            page_skin=topic.profile.topic_colour_scheme,
        )
        form = feed_import_form()

        get_page("tool_form", context, topic, form)

    def POST(self, topic_id): 
        user = login_through()
        if not user:
            return

        topics, topic = model.t_helper(topic_id)

        context = Storage(title=_("New feed for ") + topic.title)
        form = feed_import_form()

        if not form.validates():
            get_page("tool_form", context, topic, form)
            return

        i = web.input(
              url="",
              description="",
              issues=None,
              freq=None,
              origin=config.origin, # origin from the form?
        )

        feed_author = i.description.strip() or _("external")
        try: freq = int(i.freq)
        except: freq = 600   # default frequency
        feed = model.Datasource(
            url=i.url.replace(" ", "").strip(),
            type=i.issues and "autoissuefeed" or "autofeed",
            adapter="",
            frequency=freq,
            description=feed_author,
        )
        model.Datasources.store(feed, topic, user)
        feed_user = auto_author_user(feed_author, user)

        model.add_points_from_feed(topic, feed, feed_user, aged=5)
        web.seeother(links("topic", topic_id))


class Datasource_edit:
    def GET(self, topic_id, ds_id): 
        user = login_through()
        if not user:
            return

        topics, topic, dss, ds = model.t_d_helper(topic_id, ds_id)

        if not acl.authorize.manage_topic(topic):
            redirect(5, _("You do not have rights for that."), 
                links("topic", topic.id))
            return

        context = Storage(
            title=_("Edit feed "),
            page_skin=topic.profile.topic_colour_scheme,
        )
        form = feed_import_form()

        i = web.input(
              url="",
              description="",
              issues=None,
              freq=None,
              origin=config.origin, # origin from the form?
        )

        form.fill(
            url=ds.url,
            issues=(ds.type == "autoissuefeed"),
            freq=ds.frequency,
            description=ds.description,
        )

        get_page("tool_form", context, topic, form)

    def POST(self, topic_id, ds_id): 
        user = login_through()
        if not user:
            return

        topics, topic, dss, ds = model.t_d_helper(topic_id, ds_id)

        context = Storage(title=_("Edit feed for ") + topic.title)
        form = feed_import_form()

        if not form.validates():
            get_page("tool_form", context, topic, form)
            return

        i = web.input(
              url="",
              description="",
              issues=None,
              freq=None,
              origin=config.origin, # origin from the form?
        )

        feed_author = i.description.strip() or _("external")
        try: freq = int(i.freq)
        except: freq = 600   # default frequency
        feed = model.Datasource(
            id=ds.id,
            url=i.url.replace(" ", "").strip(),
            type=i.issues and "autoissuefeed" or "autofeed",
            frequency=freq,
            description=feed_author,
            adapter=ds.adapter,
        )
        model.Datasources.update(feed, topic, user)
        feed_user = auto_author_user(feed_author, user)
        model.add_points_from_feed(topic, feed, feed_user, aged=5)
        web.seeother(links("topic", topic_id))

###############################################################################
# UM SETTINGS PAGE
###############################################################################

def settings_form():
    return form.Form( 
    form.Fieldset('fieldset', description=_("Enter configuration parameter")),
    form.Textbox("property_key",
        form.required,
        form.Validator(_('Must be filled'), lambda x:x.strip()),
        description=_("Parameter name"),
    ), 
    form.Textbox("property_value",
        form.required,
        description=_("Value"),
        size=60,
    ), 
    form.Dropdown("language",
        [''] + config.LANGUAGES,  # !!! better names
        form.Validator(_('Language not supported'), 
                        lambda x: x == "" or x in config.LANGUAGES),
        description=_("Language"),
        size=1,
    ), 
    form.Fieldset('end_of_fieldset'),
    )()

def settings_form_large():
    return form.Form( 
    form.Fieldset('fieldset', description=_("Enter configuration parameter")),
    form.Textbox("property_key",
        form.required,
        form.Validator(_('Must be filled'), lambda x:x.strip()),
        description=_("Parameter name"),
    ), 
    form.Textarea("property_value",
        form.required,
        description=_("Value"),
        cols=80, rows=10,
    ), 
    form.Dropdown("language",
        [''] + config.LANGUAGES,  # !!! better names
        form.Validator(_('Language not supported'), 
                        lambda x: x == "" or x in config.LANGUAGES),
        description=_("Language"),
        size=1,
    ), 
    form.Fieldset('end_of_fieldset'),
    )()

def settings_form_editor():
    return form.Form( 
    form.Fieldset('fieldset', description=_("Enter configuration parameter")),
    form.Textbox("property_key",
        form.required,
        form.Validator(_('Must be filled'), lambda x:x.strip()),
        description=_("Parameter name"),
    ), 
    form.Editor("property_value",
        form.required,
        description=_("Value"),
    ), 
    form.Dropdown("language",
        [''] + config.LANGUAGES,  # !!! better names
        form.Validator(_('Language not supported'), 
                        lambda x: x == "" or x in config.LANGUAGES),
        description=_("Language"),
        size=1,
    ), 
    form.Fieldset('end_of_fieldset'),
    )()


def get_settings():
    settings = [model.Storage(language=k[0], key=k[1], value=v)
        for k, v in get_dynamic_profile().items()]
    settings.sort(key=lambda x:(x.key, x.language))
    return settings


class Settings:

    def GET(self):
        """
        UM settings page. Also handles edit and setting default value.
        """
        user = login_through()
        if not user:
            return

        if not acl.authorize.change_um_settings():
            redirect(5, _("You do not have rights to edit settings."), 
                links.index)
            return

        presets = web.input(key="", value="", language="", default=None)

        if presets.default:
            import default_config
            try:
                value = getattr(default_config, presets.key)
                if presets.language:
                    value = value[language]
            except:
                raise
            presets.value = value

        context = Storage(
            title = _("Urban Mediator Settings"),
        )

        if presets.key.startswith("doc_"):
            if presets.value:
                file_key = "DOCS/" + presets.value.split("/")[1]
                try:
                    presets.value = media.file_storage.getItem(file_key, mode="str")
                except:
                    pass   # file lost?!
            form = settings_form_editor()
        elif "\n" in presets.value or len(str(presets.value)) > 60:
            form = settings_form_large()
        else:
            form = settings_form()
        form.fill(
            language=presets.language,
            property_key=presets.key,
            property_value=presets.value,
        )

        get_page('settings', context, get_settings(), form)

    def POST(self):

        user = login_through()
        if not user:
            return

        if not acl.authorize.change_um_settings():
            redirect(5, _("You do not have rights to edit settings."), 
                links.index)
            return

        context = Storage(
            title = _("Urban Mediator Settings"),
        )

        form = settings_form()
        validates = form.validates()

        if not validates:
            get_page("settings", context, get_settings(), form, 
                error_message=_("Some fields were not entered correctly:"))
            return
        else:
            profile = get_dynamic_profile()
            lang = form.d.language or None
            property_key = form.d.property_key
            property_value = form.d.property_value
            if property_key.startswith("doc_"):
                if property_value:
                    property_value = media.storeMediaFile(property_value, prefix="DOCS/")
            try:
                set_config_item(lang, property_key, property_value)
            except ValueError, error_message:
                get_page("settings", context, get_settings(), form, 
                    error_message=_(error_message))
                return

            profile[(lang, property_key)] = property_value


        web.seeother(links.settings)

class Topic_deletecomment:
    def GET(self, topic_id, comment_id):

        user = login_through()
        if not user:
            return

        topics, topic, comments, comment = \
            model.t_c_helper(topic_id, comment_id)

        if not acl.authorize.manage_topic(topic):
            redirect(5, _("You do not have rights to delete the widget."), 
                links("topic", topic.id))
            return

        comments.hide()

        web.seeother(links('topic_tools', topic.id))


class Topic_editcomment:
    def GET(self, topic_id, comment_id):

        user = login_through()
        if not user:
            return

        topics, topic, comments, comment = \
            model.t_c_helper(topic_id, comment_id)

        if not acl.authorize.manage_topic(topic):
            redirect(5, _("You do not have rights to change the widget."), 
                links("topic", topic.id))
            return

        print topic, comment
        return

######## TRIGGERS #################################################

def trigger_form():
    return form.Form( 
    form.Fieldset('fieldset', description=_("Enter trigger information")),
    form.Textbox("description",
        description=_("Describe the trigger"),
    ), 
    form.Textbox("condition",
        description=_("Condition (e.g. addpoint)"),
        value="triggertest",
    ), 
    form.Textbox("action",
        description=_("Action"),
        value="test",
    ), 
    form.Textbox("adapter",
        description=_("Adapter"),
        value="test",
    ), 
    form.Textbox("url",
        description=_("URL (as a parameter for the adapter)"),
    ), 
    form.Fieldset('end_of_fieldset'),
    )()


class Trigger_delete:
    def GET(self, topic_id, trigger_id):
        topics, topic, triggers, trigger = \
            model.t_tr_helper(topic_id, trigger_id)

        user = login_through()
        if not user:
            return

        if acl.authorize.manage_topic(topic):
            triggers.delete()

        web.seeother(links('topic', topic.id))

class Trigger_edit:
    def GET(self, topic_id, trigger_id):
        user = login_through()
        if not user:
            return

        topics, topic, triggers, trigger = model.t_tr_helper(topic_id, trigger_id)

        if not acl.authorize.manage_topic(topic):
            redirect(5, _("You do not have rights for that."), 
                links("topic", topic.id))
            return

        context = Storage(
            title=_("Edit trigger "),
            page_skin=topic.profile.topic_colour_scheme,
        )
        form = trigger_form()

        i = web.input(
              description="",
              condition="",
              action="",
              adapter="",
              url="",
        )

        form.fill(
            description=trigger.description,
            condition=trigger.trigger_condition,
            action=trigger.trigger_action,
            adapter=trigger.adapter,
            url=trigger.url,
        )

        get_page("tool_form", context, topic, form)

    def POST(self, topic_id, trigger_id): 
        user = login_through()
        if not user:
            return

        topics, topic, triggers, trigger = model.t_tr_helper(topic_id, trigger_id)

        context = Storage(title=_("Edit trigger for ") + topic.title)
        form = trigger_form()

        if not form.validates():
            get_page("tool_form", context, topic, form)
            return

        i = web.input(
              description=trigger.description,
              condition=trigger.trigger_condition,
              action=trigger.trigger_action,
              adapter=trigger.adapter,
              url=trigger.url,
        )

        trigger = model.Trigger(
            id=trigger.id,
            url=i.url.replace(" ", "").strip(),
            trigger_action=i.action,
            trigger_condition=i.condition,
            description=i.description,
            adapter=i.adapter,
        )
        model.Triggers.update(trigger, topic, user)
        web.seeother(links("topic_tools", topic_id))
        return


class Topic_addtrigger:
    def GET(self, topic_id): 
        user = login_through()
        if not user:
            return

        topics, topic = model.t_helper(topic_id)
        context = Storage(
            title=_("New trigger for ") + topic.title,
            page_skin=topic.profile.topic_colour_scheme,
        )
        form = trigger_form()

        get_page("tool_form", context, topic, form)

    def POST(self, topic_id): 
        user = login_through()
        if not user:
            return

        topics, topic = model.t_helper(topic_id)

        context = Storage(title=_("New trigger for ") + topic.title)
        form = trigger_form()

        if not form.validates():
            get_page("tool_form", context, topic, form)
            return

        i = web.input(
              description="",
              condition="",
              action="",
              adapter="",
              url="not_entered",
        )

        if i.description:
            trigger = model.Trigger(
                trigger_condition=i.condition, 
                trigger_action=i.action,
                adapter=i.adapter,
                description=i.description,
                url=i.url,
            )
        else:
            web.seeother(links("topic_tools", topic_id, message=_("Error adding trigger")))
            return
        model.Triggers.store(trigger, topic, user)

        web.seeother(links("topic_tools", topic_id))
        return



######## SELFTEST #################################################

class Selftest:

    tables = "locations notes datasources tags triggers users groups".split()

    def test_page(self, name, url):
        print name,
        try:
            t1 = time.time()
            u = urllib.urlopen(url).read()
            t2 = time.time()
            print "...served in ", t2-t1, "s. ",
            print "(len = ", len(u), "bytes)"
        except:
            print "FAILED!"

    def GET(self):

        # user
        print "*" * 80
        user = get_user()
        print "User:", user

        print "*" * 80

        # database
        print "Database connection",
        try:
            import database
            items = database.check_connection()
            print "...ok"
        except:
            print "FAILED. Further tests impossible"
            return

        try:
            import database
            print "Database layout version"
            items = database.version()[0].items()
            for k, v in items:
                print k, v
        except:
            print "FAILED. CREATE TABLES FIRST. Further tests impossible"
            return

        print "*" * 80

        print "Database (low-level) statistics"
        for table in sorted(self.tables):
            print table, ":", database.num_of_records(table)[0].count

        print "Locations"
        print "%10s : %10s : %10s : %10s" % ("type", "origin", "visible", "count")
        for r in database.locations_stats():
            print "%10s : %10s : %10s : %10s" % (r.type, r.origin, r.visible, r.count)

        print "*" * 80
        print "Timings"
        self.test_page("Main", links.index)
        self.test_page("Mobile", mobile_links.map)

        print "*" * 80

        print "Model statistics"
        print "Points:", len(model.Points())
        print "Topics (aka boards aka projects):", len(model.Projects())
        print "Tags:", len(model.Tags())

        print "*" * 80
        print "Configuration:"

        profile = get_dynamic_profile()
        for k, v in profile.items():
            lang = k[0] and ("[%s] " % k[0]) or ""
            key = k[1]
            if key in "getmap_server,getmap_custom_server":
                print "%s%s" % (lang, key), "=", "*NOT SHOWN*"
            else:
                print "%s%s" % (lang, key), "=", v

        print "*" * 80
        print "Extras:"

        try:
            import pyproj
            print "pyproj available, version: ", pyproj.__version__
        except:
            print "pyproj not available"

        print "*" * 80
        print "OS stats"
        try:
            import os
            print "Load averages:", os.getloadavg()
        except:
            print "FAILED"

class StaticMedia:

    def GET(self, urlpath):
        file_key = url_handler.translate_path(urlpath)
        print media.downloadStaticMediaFile(file_key, 
                                base_dir=config.static_dir)


### Hack to get long values correctly handled

import web.db

def sqlify(obj):
    import datetime
    if obj is None:
        return 'NULL'
    elif obj is True:
        return "'t'"
    elif obj is False:
        return "'f'"
    elif datetime and isinstance(obj, datetime.datetime):
        return repr(obj.isoformat())
    elif isinstance(obj, long):
        return str(obj)
    else:
        return repr(obj)

web.db.sqlify = sqlify   #!!!

### end of hack


web.template.Template.globals.update(dict(
    pc_links=links,
    user_groups=get_user_groups,
    user_belongs_to=user_belongs_to,
    acl=acl,
))


def get_dynamic_profile():
    if not hasattr(config, "dynamic_profile"):
        import um_profile
        config.dynamic_profile = um_profile.Profile()
    return config.dynamic_profile

def set_config_item(lang, key, value):
    """ Set item for the use from config """
    newvalue = value
    oldvalue = getattr(config, key, None)
    if oldvalue is None:
        raise ValueError, "Unknown parameter"
    if not lang:
        if isinstance(oldvalue, bool):
            newvalue = newvalue.lower() not in ('0', 'false', 'no', '')
        elif isinstance(oldvalue, tuple) or isinstance(oldvalue, list):
            newvalue = newvalue.split(",")
        else:
            newvalue = type(oldvalue)(newvalue)
        setattr(config, key, newvalue)
    else:
        if isinstance(oldvalue, dict):
            oldvalue[lang] = newvalue
        else:
            raise ValueError, "Language specifier not needed"

def settings_defaults():
    """ Iterator for default config values. 
        Even if the concrete value is not used,
        key is used to indicate that there should be such a 
        key-value pair in the config and value has the type
        specified in default_config.
    """
    import default_config
    for k in dir(default_config):
        if not k.startswith("_"):
            value = getattr(config, k)   #!!!
            if isinstance(value, bool) or isinstance(value, int):
                value_repr = str(int(value))
            elif isinstance(value, float):
                value_repr = repr(value)
            elif isinstance(value, tuple) or isinstance(value, list):
                value_repr = ",".join(value)
            elif isinstance(value, dict):
                for lang, dict_value in value.items():
                    yield model.Storage(
                        language=lang,
                        key=k,
                        value=dict_value,
                    )
                continue
            else:
                value_repr = value
            yield model.Storage(
                language=None,
                key=k,
                value=value_repr,
            )

def update_config():
    """Update config from profile but
    also profile is some parameter is missing.
    default_config.py has default values.
    """
    profile = get_dynamic_profile()
    for s in settings_defaults():
        if profile.has_key((s.language, s.key)):
            set_config_item(s.language, s.key, profile[(s.language, s.key)])
        else:
            profile[(s.language, s.key)] = s.value

def main():
    web.db.connect(**config.db_parameters)
    update_config()
    web.run(urls, globals(), *config.middleware)

if __name__ == "__main__":
    main()

