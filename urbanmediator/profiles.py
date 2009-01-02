# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Data for the default profiles.
"""


import config
from links import *
from web.utils import Storage

TOPIC_ORDERS = config.main_page_topic_orders
POINT_ORDERS = config.main_page_point_orders
# for gettext  _("newest"), _("oldest"), _("recently updated"), _("most points"), _("title")

DEFAULT_TOPIC_BASIC_PROFILE = Storage(
    topic_icon=pc_links('default_topic_icons',
                    config.topic_icons.split()[0]),
    topic_colour_scheme="A",
)

DEFAULT_TOPIC_ADVANCED_PROFILE = Storage(
    default_view_mode="list",  # "map"
    default_view_order="recently updated",  # "map"
    point_list_show="title,added,url,description-full,author,tags",
    topic_page_elements="new point button,widgets,hr,search,tagcloud,hr,triggers",
    # "search,tagcloud,hr,new point button,widgets,hr,triggers,about",
    topic_point_comments_elements = "comments,pagination,addcomment,feed",
    topic_point_page_contents = "title,description,author,added,url,tags,addtag,comments",
    point_contributors="visitors",  # anyone,visitors,administrators,nobody
        # specifies minimum right holder (thus, all after also get it)
    topic_owner_rights="topic_only", # or "topic_and_points"

    getmap_layers="",
    getmap_layers1="",
    getmap_layers2="",
    getmap_zoom1="",
    getmap_zoomshift="",
    getmap_zoom2="",
    getmap_params="",
    getmap_custom="",
)

DEFAULT_TOPIC_PROFILE = Storage()
DEFAULT_TOPIC_PROFILE.update(DEFAULT_TOPIC_BASIC_PROFILE)
DEFAULT_TOPIC_PROFILE.update(DEFAULT_TOPIC_ADVANCED_PROFILE)


DEFAULT_POINT_PROFILE = Storage(
    #???
)

DEFAULT_COMMENT_PROFILE = Storage(
    #???
)

DEFAULT_USER_PROFILE = Storage(
    email="",
)

