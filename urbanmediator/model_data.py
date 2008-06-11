# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    This module contains the data classes for the
    domain model of the Urban Mediator
"""

import datetime

class Entity(dict):
    """ This is replica of web.utils.Storage changed for
    representing data object in the model
    """
    def __getattr__(self, key): 
        try: return self[key]
        except KeyError, k: raise AttributeError, k
    def __setattr__(self, key, value): self[key] = value
    def __delattr__(self, key):
        try: del self[key]
        except KeyError, k: raise AttributeError, k
    def __repr__(self):
        return self.__class__.__name__ + "(" + dict.__repr__(self) + ")"

class Point(Entity):
    """
    # From the database
    id = None
    lat = None
    lon = None
    title = ''
    added = None           # datetime
    user_id = None
    origin = ''
    ranking = 0
    url = ''
    type = 'point'
    visible = 1

    # Calculated
    comments_count = 0     # optional
    last_comment = None    # datetime, optional
    distance = 0           # optional
    tags = None            # []
    url = None
    """

class Comment(Entity):
    """
    # From the database
    id = None
    location_id = None
    text = ""
    added = None  #datetime
    user_id = None
    origin = ''
    ranking = 0

    # Calculated
    lat = None
    lon = None
    location_title = ""
    author = ""
    """

class Tag(Entity):
    """
    # From the database
    id                   # optional
    tag
    tag_namespace = ''   # e.g. official
    tag_system_id        # URL for tag schema
    ns_tag               # tag representation  NS:TAG
    count_locations      # optional
    count_users          # optional
    username             # optional

    # Calculated
    safetag         # (view-specific) optional, safe representation of tag
    safe_ns_tag     # (view-specific) optional, safe representation of ns_tag
    """

    STOP_LIST = """ja hakusanat avainsanat tai on and"""

class User(Entity):
    """
    id                    # optional
    username
    groups
    """

class MapInfo(Entity):
    """
    id                    # optional
    name
    engine
    """

class Project(Entity):
    """
    # From the database
    id = None
    lat = None   #optional
    lon = None   #optional
    title = ''
    added = None           # datetime
    user_id = None
    origin = ''
    ranking = 0
    url = ''
    type = 'project'
    visible = 1

    # Calculated
    comments_count = 0     # optional
    last_comment = None    # datetime, optional
    distance = 0           # optional
    tags = None            # []
    url = None
    """


class Datasource(Entity):
    """
    id INT NOT NULL AUTO_INCREMENT,
    type VARCHAR (30) DEFAULT '', -- "feed", "scrape", "api query", etc
    -- adapter VARCHAR (128) DEFAULT '', -- module used to fetch, like specific scraper
    url VARCHAR(255) NOT NULL DEFAULT '',
    frequency INT DEFAULT 86400,     -- how frequently fetched, s
    description TEXT,  -- human readable description
    -- private INT DEFAULT 0, -- True/False
    -- credentials VARCHAR(255) NOT NULL DEFAULT '', -- to access the resource
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    """

class Category(Tag):
    """
    title = ''
    
    # calculated:
    projects  OR
    points
    """


class Collection:
    """Class for representing collections of items """

    _contents = None

    def filter_by_id(self, id):
        self._contents = [p for p in self._contents 
                            if str(p.id) == str(id)]

    def reverse(self):
        self._contents.reverse()

    def limit_by(self, n, m=None):
        self._contents = self.list(n, m)

    def list(self, n=None, m=None):
        if n is not None and m is not None:
            return self._contents[n:m]
        if n is not None:
            return self._contents[:n]
        return self._contents

    def page(self, n, length=24):
        """Give a page number n with a given length. Integer 1, 2, ...
        """
        if n < 0:
            n += self.num_of_pages() + 1 
        return self._contents[(n-1)*length:n*length]

    def limit_by_page(self, n, length=24):
        """Restrict items to one page only
        """
        self._contents = self.page(n, length)

    def num_of_pages(self, length=24):
        return (len(self)-1)//length + 1

    def item_id(self, item):
        """Overridable!"""
        return str(item["id"])

    def set(self):
        return set([self.item_id(p) for p in self._contents])

    def filter_by_func(self, func):
        self._contents = [p for p in self._contents if func(p)]

    def filter_by_excluding_set(self, a_set):
        self._contents = [p for p in self._contents if self.item_id(p) not in a_set]

    def filter_by_set(self, a_set):
        self._contents = [p for p in self._contents if self.item_id(p) in a_set]

    def __len__(self):
        return len(self._contents)

    def len(self):
        return len(self._contents)

    count = len

    def __iter__(self):
        return iter(self._contents)

    def __repr__(self):
        return str(self.list())


class Group(Entity):
    """
    id                    
    """

class Trigger(Entity):
    """
    id int(11) NOT NULL auto_increment,
    project_id int(11) default NULL,
    user_id int(11) default NULL,
    condition varchar(128) default '',  -- to be defined. 'addpoint', etc
    trigger_action text NOT NULL default '',
    adapter varchar(128) default '',
    url varchar(255) NOT NULL default '',
    frequency int(11) default '86400',
    description text,
    added timestamp NOT NULL default CURRENT_TIMESTAMP,
    """

class Indicators(Entity):
    """
    """

class Profile(Entity):
    """
       for user profiles, object (projects) profiles
    """

