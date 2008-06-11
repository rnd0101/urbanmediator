# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Registry for links.
"""

import config, util

base_url = config.base_url
schema_base_url = config.schema_base_url + "/"

############## base links ###############################
base = base_url + '/'
pc_links = util.Links({
    'base_url': base_url,
    'static': schema_base_url,
    'fckeditor_base': schema_base_url + "fckeditor/",
    'sitemap': base + "sitemap.xml",
    'index': base + 'index.html',
    'search': base + 'search.html',
    'map_search': base + "map_search.html",
    'guide': base + 'guide/%s.html',
#
    'new_topic': base + "newtopic.html",
    'topic': base + 'topic/%s',
    'topic_newpoint': base + 'topic/%s/new_point',
    'topic_tools': base + 'topic/%s/tools',
    'topic_widgets': base + 'topic/%s/widgets',
    'topic_addwidget': base + 'topic/%s/addwidget',
    'topic_adminlist': base + 'topic/%s/adminlist',
    'topic_settings': base + 'topic/%s/settings',
    'topic_feedback': base + 'topic/%s/feedback',
    'topic_advanced': base + 'topic/%s/advanced',
    'topic_location': base + 'topic/%s/location',
    'topic_delete': base + 'topic/%s/delete',
    'topic_subscription': base + 'topic/%s/subscription',

    'tools_submit_widgetize': base + 'topic/%s/tools/submit_widgetize',
    'tools_note_widgetize': base + 'topic/%s/tools/note_widgetize',
    'tools_map_widgetize': base + 'topic/%s/tools/map_widgetize',
    'tools_container_widgetize': base + 'topic/%s/tools/container_widgetize',
    'tools_topic_points_widgetize': base + 'topic/%s/tools/topic_points_widgetize',
    'tools_topic_links_widgetize': base + 'topic/%s/tools/topic_links_widgetize',
    'tools_widget_editor': base + 'topic/%s/tools/widget_editor',
    'tools_widget_move': base + 'topic/%s/tools/widget_move',

    'tools_widgets': base + 'topic/%s/tools/widgets',
    'topic_delcomment': base + 'topic/%s/comment/%s/delete',
    'topic_editcomment': base + 'topic/%s/comment/%s/edit',

    'topic_addtrigger': base + 'topic/%s/addtrigger',
    'topic_deltrigger': base + 'topic/%s/trigger/%s/delete',
    'topic_edittrigger': base + 'topic/%s/trigger/%s/edit',

    'tools_feed_import': base + 'topic/%s/tools/feed_import',
    'editor_base_url': schema_base_url + "fckconfig.js",
    'user': base + 'user/%s',

    'user_tools': base + 'user/%s/tools',
    'user_settings': base + 'user/%s/settings',
    'user_location': base + 'user/%s/location',

    'settings': base + 'settings.html',
    'edit_doc': base + 'edit_doc.html',

    'point': base + 'topic/%s/point/%s',
    'point_addtag': base + 'topic/%s/point/%s/addtag',
    'point_delete': base + 'topic/%s/point/%s/delete',
    'point_mark': base + 'topic/%s/point/%s/mark',
    'point_addcomment': base + 'topic/%s/point/%s/addcomment',
    'point_settings': base + 'topic/%s/point/%s/settings',
    'point_editcomment': base + 'topic/%s/point/%s/comment/%s/edit',
    'point_deletecomment': base + 'topic/%s/point/%s/comment/%s/delete',

    'topic_ds_edit': base + 'topic/%s/ds/%s/edit',
    'topic_ds_delete': base + 'topic/%s/ds/%s/delete',
    'page_skin': schema_base_url + "css/scheme%s.css",
    'skindemo': base + "skindemo",

    'searchtopic': base + 'topic/%s',
    'user': base + 'user/%s',
    'logout': base + 'logout.html',
    'login': base + 'login.html',
    'signup': base + 'signup.html',
    'about': base + 'about.html',
    'help': base + 'help.html',
    'feedback': base + 'feedback',
    'privacy': base + 'privacy.html',
    'contact': base + 'contact.html',
    'redirect': base + 'redirect.html',
    'alert': base + 'alert.html',
    'getmap': base + 'getmap',
    'img': schema_base_url + 'img/',
    'set_language_action': base + 'setlang',
    'default_topic_icons' : schema_base_url + 'img/topicicon_default/',
})


############## feed links ###############################
base = base_url + "/feed/"
feed_links = util.Links({
    'base_url': base_url,
    'static': schema_base_url,
    'opml': base + "opml.xml",
    'topics': base + "topics",
    'user_topics': base + "user/%s/topics",
    'search': base + "search",
    'topic_points': base + "topic/%s/points",
    'point_comments': base + "topic/%s/point/%s/comments",
    'topic_as_csv': base + "topic/%s.csv",
    'json_search': base + "json/search",
})


############## mobile links ###############################
base = base_url + '/mobile/'
mobile_links = util.Links({
    'base_url': base,
    'static': schema_base_url,
    'index': base,
    'help': base + 'help.html',
    'about': base + 'about.html',
    'locationmap': base + 'locationmap',
    'locationmaprepr': base + 'locationmaprepr',
    'map_action': base + 'map_action.html',
    'locationmapclean': base + 'locationmapclean',
    'home': base,
    'point_list': base + 'point_list.html',
    'add_point': base + 'add_point.html',
    'place': base + 'place.html',
    'map': base + 'map.html',
    'search': base + 'search.html',
    'info': base + 'info.html',
    'point': base + 'point.html',
    'login': base + 'login',
    'logout': base + 'logout',
})

############## widget links ###############################
base = base_url + '/widget/'
widget_links = util.Links({
    'base_url': base_url,
    'static': schema_base_url,
    'submit': base + 'topic/%s/submit',
    'note': base + 'topic/%s/note',
    'map': base + 'topic/%s/map',
    'topic_points': base + 'topic/%s/topic_points',
    'topic_links': base + 'topic/%s/topic_links',
    'container': base + 'topic/%s/container',
})
