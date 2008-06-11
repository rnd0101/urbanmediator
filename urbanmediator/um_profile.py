# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Module to deal with UM profile stored in the database.
    It should be importable from config, so config itself 
    can't be used here.

"""

import web
from util import EntityMixin
from UserDict import DictMixin

class Profile(DictMixin, EntityMixin):
    """ Kind of persistent dictionary with languages
    However, cache may have some left values if 
    language is inconsistently given/not given, as e.g. in:

    ump[("en", "myprof")] = "123"
    del ump["myprof"]

    This is done to make the dict work faster.

    """
    def __init__(self):
        # language-specific things
        self.__dict__["_data"] = dict([((p.lang, p.prop_key), p.prop_value) 
            for p in web.query(
                """SELECT lang, prop_key, prop_value FROM profile;""")
        ])

    def __getitem__(self, key):
        if not isinstance(key, tuple):
            key = None, key
        try:
            return self.__dict__["_data"][key]
        except KeyError:
            # try default without a language
            return self.__dict__["_data"][(None, key[1])]
        
    def __setitem__(self, key, item):
        # this should be transaction, but is ok as
        # profile should not be edited by many people at once
        self.__delitem__(key)
        if not isinstance(key, tuple):
            key = None, key
        web.query("""INSERT INTO profile (lang, prop_key, prop_value) 
                    VALUES ($lang, $prop_key, $prop_value);""", 
                  vars=dict(lang=key[0], prop_key=key[1], prop_value=item))
        self.__dict__["_data"][key] = item

    def __delitem__(self, key):
        if not isinstance(key, tuple):
            key = None, key
        web.query("""DELETE FROM profile 
                WHERE lang=$lang AND prop_key=$prop_key;""", 
                vars=dict(lang=key[0], prop_key=key[1],))
        try:
            del self.__dict__["_data"][key]
        except:
            pass  # no problem if the key is not there

    def keys(self):
        return self.__dict__["_data"].keys()

