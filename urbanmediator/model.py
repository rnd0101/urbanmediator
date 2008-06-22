# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    This module contains the domain model of the Urban Mediator,
    abstracting "controllers"  and "views" from datasource queries,
    merging data, etc.
"""

from model_data import Entity, Point, Comment, Tag, User, Group, Trigger, Indicators, \
                       Project, Datasource, Collection, Category, Profile
from feed_data import fetch_feed, fetch_enclosure
from plugins import geocoding
import database
import config
import itertools
import re, math
import datetime
import media, mail_parser
import triggers
import util
import geo_support
import url_handler
import wsse
from profiles import *

def object_by_id(object_id):
    p = database.object_by_id(object_id)
    if not p:
        return []
    p = p[0]
    if p.type == 'project':
        return [Project(p)]
    else:
        return [Point(p)]

def object_by_id_hard(object_id):
    p = database.object_by_id_hard(object_id)
    if not p:
        return []
    p = p[0]
    if p.type == 'project':
        return [Project(p)]
    else:
        return [Point(p)]

def point_by_id(point_id):
    p = database.point_by_id(point_id)
    if not p:
        return []
    p = p[0]
    return [Point(p)]

def point_by_id_hard(point_id):
    p = database.point_by_id_hard(point_id)
    if not p:
        return []
    p = p[0]
    return [Point(p)]

def project_by_id(point_id):
    p = database.project_by_id(point_id)
    if not p:
        return []
    p = p[0]
    return [Project(p)]

def comment_by_id(comment_id):
    c = database.comment_by_id(comment_id)
    if not c:
        return []
    c = c[0]
    return [Comment(c)]

def user_by_id(user_id):
    u = database.user_by_id(user_id)
    if not u:
        return []
    u = u[0]
    return [User(u)]

def user_by_username(user_username):
    u = database.user_by_username(user_username)
    if not u:
        return []
    u = u[0]
    return [User(u)]


def internal_points(tags=None, project=None, only_visible=True, limit=None):
    if tags:
        if project is None:
            db_points = database.points_by_tags([(t.tag_namespace, t.tag)
                                                for t in tags.list()])
        else:
            db_points = database.points_by_project_and_tags(
                                project,
                                [(t.tag_namespace, t.tag)
                                 for t in tags.list()])
    else:
        if project is None:
            db_points = database.points()
        else:
            db_points = database.points_by_project(project, limit=limit)
#    if only_visible:
#        return [Point(p) for p in db_points if p.visible]
    return [Point(p) for p in db_points]

def search_points(search_query, project=None):
    tags = Tags(search_query.lower())
    if project is None:
        db_points = database.search_locations(search_query.strip().lower(),
                [(t.tag_namespace, t.tag) for t in tags.list()],
                loctype='point')
    else:
        db_points = database.search_locations_of_project(search_query.strip().lower(),
                [(t.tag_namespace, t.tag) for t in tags.list()],
                project=project, loctype='point')
    return [Point(p) for p in db_points]

def search_projects(search_query):
    tags = Tags(search_query.lower())
    db_points = database.search_locations(search_query.strip().lower(),
                [(t.tag_namespace, t.tag) for t in tags.list()],
                loctype='project')
    return [Point(p) for p in db_points]

def internal_projects(tags=None, point=None):
    if point:
        if tags:
            db_points = database.projects_by_point_and_tags(point,
                         [(t.tag_namespace, t.tag) for t in tags.list()])
        else:
            db_points = database.projects_by_point(point)
    else:
        if tags:
            db_points = database.projects_by_tags([(t.tag_namespace, t.tag)
                          for t in tags.list()])
        else:
            db_points = database.projects()
    # later, there will be a need to indicate that the point is
    # internal. by URL?
    return [Project(p) for p in db_points]


def need_to_load_ds(url, aged):
    """Check if specific datasource needs to be loaded again"""
    # its same dir as for URLs
    return url_handler.needToReloadURL(url, aged=aged)  # cache_dir?

def external_points(tags=None, urls=None, aged=None, origin='external'):
    """
    Making a list of points from a feed. Points are not 
    completely equivalent to the points from the database,
    e.g. id is 0.
    """
    feed_points = []
    if tags:
        tags = Tags(tags)
        tagset = tags.set()
    for e in fetch_feed(urls=urls, aged=aged):
        e["tags"] = Tags(e.get("tags", ""))
        if tags and not (e["tags"].set() & tagset):
            continue
        for k, v in e.items():
            if isinstance(v, unicode):
                e[k] = e[k].encode("utf-8")

        if not e.has_key("url"):
            e["url"] = ''
        e["id"] = 0
        e["ranking"] = 1
        e["distance"] = 0
        e["last_comment"] = ''
        e["comments_count"] = 0
        e["origin"] = origin
        e["description"] = e["text"]  # ?
        feed_points.append(Point(e))
    return feed_points


class UM:
    @staticmethod
    def title(lang="en"):
        try:
            return config.instance_name[lang]
        except:
            return config.instance_name["en"]

SELF_ASSIGNABLE_ROLES = set(["subscribed"])

class Points(Collection):

    def __init__(self,
                 internal=True,
                 external=None,
                 project=None,
                 tags="",
                 id=None,
                 user=None,
                 by_user=None,
                 by_comment=None,
                 only_visible=True,
                 search_query="",
                 nearby=None,
                 aged=None,
                 properties=None,
                 limit=None):
        """ If id is given, Points will contain just one (or zero)
        points with given id.
        tags is a tag string.
        """
        if id == 0:
            self._contents = []
        elif id:
            self._contents = point_by_id(id)
            self.annotate_by_tags()
            self.annotate_by_comments()
        elif nearby:
            lat, lon, radius, limit = nearby
            self._contents = [Point(p) for p in 
                database.points_nearby(lat, lon, radius, limit, project)]
        elif search_query:
            self._contents = search_points(search_query, project=project)
            self.filter_dups()
        elif by_user is not None:
            self._contents = [Point(p) for p in 
                database.points_by_user(by_user)]
        elif by_comment is not None:
            self._contents = [Point(p) for p in 
                database.points_by_comment(by_comment)]
        else:
            tags = Tags(tags)
            instructions = tags.extract_instructions()
            if project is not None:
                internals = internal and internal_points(tags, 
                                     project=project,
                                     only_visible=only_visible, limit=limit) or []
            else:
                internals = internal and internal_points(tags, 
                                     only_visible=only_visible) or []
            if external is True:
                externals = external and external_points(tags) or []
            elif external:
                externals = external_points(tags, urls=external, aged=aged)
            else:
                externals = []
            self._contents = internals + externals
            if "filter:radius" in instructions:
                try:
                    radius = float(instructions["filter:radius"])
                    lat = float(instructions["filter:lat"])
                    lon = float(instructions["filter:lon"])
                    self.filter_by_distance(lat, lon, max_distance=radius)
                    if properties is not None:
                        properties.update(dict(lat=lat, lon=lon, radius=radius))
                except:
                    pass  # silently ignore

        self.annotate_by_repr_coordinates()

    @staticmethod
    def store(point, user, project=None):
        if not hasattr(point, "id") or not point_by_id_hard(point.id):  # we have new point
            point.id = database.point_insert(point, user)
        if not hasattr(point, "uuid"):  # fix uuid for internal point
            point.uuid = "%s" % point.id
            database.point_update(point, user)

        if project is not None:
            database.update_projects_points(project, point)

    @staticmethod
    def create(user, name, lat, lon, url, origin, tags, 
               description='', address='', project_id=None,
               attachments=None, deferred=False, fileinfo={}):
        """
        user - author, 
        deferred - if True, point should be not visible
        """

        res = geocoding_helper(address, onfail=(0.0, 0.0),
            metadata={'hint_lat': float(config.center_lat),
                      'hint_lon': float(config.center_lon),})
        if res.lat:
            lat = res.lat
            lon = res.lon

        point = Point(title=name, lat=lat, lon=lon, url=url, origin=origin, visible=not deferred)
        Points.store(point, user)

        if attachments:
            for a in attachments:
                pass


        attachment = Storage()
        try:
            fc = fileinfo.file.read()
            if fc:
                attachment = Storage(
                    file_contents=fc,
                    filename=fileinfo.filename,
                    content_type=media.guess_content_type(fileinfo.filename),
                )
                media_url = media.uploadMediaFile(**attachment)
                description += media_file_html(media_url)
        except:
            pass

        if description:
            comment = Comment(text=description, origin=origin, type="comment")
            Comments.store(comment, point, user)
#    i.p_category.strip()
#    if i.p_category:
#         tags = model.Tags(i.p_category)
#         tags.tag_point(point, user)

        tags = Tags(tags)
        tags.make_safe()
        if tags:
            tags.tag_point(point, user)

        if project_id is not None:
            projects = Projects(id=int(project_id))
            project = projects.first_item()
            Points.store(point, user, project)
            point.description = description + POINT_ID_FORMAT % (config.base_url, project_id, point.id)
        point.tags = tags

        if project_id is not None and not deferred:
            check_triggers(project, "addpoint", 
                point=point,
                user=user,
                attachment=attachment,
            )

        if project_id and url:
            datasource = Datasource(
                type="link",
                adapter="",
                url=url,
                frequency=0,
                description=name, )
            database.datasource_insert(datasource, project, user)

        return point

    @staticmethod
    def update(user, point, point_description, tags, fileinfo={},
            guard_special_tags=True):
        # adding possible file
        try:
            fc = fileinfo.file.read()
            if fc:
                media_url = media.uploadMediaFile(fc,
                                  filename=fileinfo.filename)
                point_description.text += media_file_html(media_url)
        except:
            pass

        # updating point itself and description
        database.point_full_update(point, user)
        Comments.update(point_description, point, user)
        # tags are trickier:
        # 1. add tags
        tags_to_add = Tags(" ".join(tags.set() - point.tags.set()))
        tags_to_add.make_safe()
        tags_to_add.tag_point(point, user)
        # 2. remove tags
        tags_to_del = Tags(" ".join(point.tags.set() - tags.set()))
        if guard_special_tags:
            tags_to_del.filter_not_in_namespaces(['special'])
        tags_to_add.make_safe()
        tags_to_del.untag_point(point, user)
        return point

    @staticmethod
    def remove_point_from_project(point, project):
        database.remove_point_from_project(point, project)

    @staticmethod
    def remove_datasource_from_project(ds, project):
        database.remove_datasource_from_project(ds, project)


    @staticmethod
    def allows(point, user, role):
        return role in Points.get_roles(point, user)

    @staticmethod
    def get_roles(point, user):
        return [p.role for p in database.get_policies(point, user)]

    @staticmethod
    def do_set_roles(point, user, roles, adder_user):
        database.set_policies(point, user, roles, adder_user)

    @staticmethod
    def set_roles(point, user, roles, adder_user):
        if not Points.allows(point, adder_user, "manage_users"):
            roles = set(roles) & SELF_ASSIGNABLE_ROLES
            if not roles:
                return None, "Not allowed"
        old_roles = set(Points.get_roles(point, user))
        roles_to_set = set(roles) - old_roles
        Points.do_set_roles(point, user, roles_to_set, adder_user)
        return True, "Success"

    @staticmethod
    def do_unset_roles(point, user, roles, adder_user):
        database.unset_policies(point, user, roles, adder_user)

    @staticmethod
    def unset_roles(point, user, roles, adder_user):
        if not Points.allows(point, adder_user, "manage_users"):
            roles = set(roles) & SELF_ASSIGNABLE_ROLES
            if not roles:
                return None, "Not allowed"
        Points.do_unset_roles(point, user, roles, adder_user)
        return True, "Success"

    def hide(self):
        try:  # !!!
            self.annotate_by_projects()
        except:
            pass
        for p in self._contents:
            try:
                check_triggers(p.first_project, "delpoint", 
                    point=p,
                )
            except:
                pass
            database.hide_point(p)

    def delete(self):
        try:  # !!!
            self.annotate_by_projects()
        except:
            pass
        for p in self._contents:
            try:
                check_triggers(p.first_project, "delpoint", 
                    point=p,
                )
            except:
                pass
            database.delete_point(p)


    def add(self, points1):
        these_points = self.set()
        for p in points1:
            if self.item_id(p) not in these_points:
                 self._contents.append(p)

    def filter_by_period(self, (begin, end)):
        if begin is None:
            self._contents = [p for p in self._contents if p.added <= end]
        if end is None:
            self._contents = [p for p in self._contents if p.added <= end]
        self._contents = [p for p in self._contents if begin <= p.added <= end]

    def filter_by_user(self, user):
        self._contents = [p for p in self._contents if p.user_id == user.id]

    def filter_by_uuid(self, uuid):
        self._contents = [p for p in self._contents if util.loc_digest(p) == uuid]

    def filter_by_visibility(self, state=1):
        self._contents = [p for p in self._contents if p.visible == state]

    def filter_dups(self):
        new_contents = []
        s = set()
        for p in self._contents:
            if p.id not in s:
                new_contents.append(p)
                s.add(p.id)
        self._contents = new_contents

    def filter_by_distance(self, lat, lon, max_distance=0):
        points = []
        for p in self._contents:
            p.distance = geo_support.dist((lat, lon), (float(p.lat), float(p.lon)))
            if not max_distance or p.distance <= max_distance:
                points.append(p)
        self._contents = points

    def annotate_by_distance(self, lat, lon):
        self.filter_by_distance(lat, lon, max_distance=0)

    def sort_by_distance(self):
        self._contents.sort(key=lambda x: x.distance)

    def sort_by_title(self):
        self._contents.sort(key=lambda x: x.title.lower())

    def sort_by_added(self):
        self._contents.sort(key=lambda x: x.added, reverse=True)

    sort_by_vitality = sort_by_added

    def filter_by_ranking(self, low_limit=-200, high_limit=200):
        self._contents = [p for p in self._contents if low_limit <= p.ranking <= high_limit]
        for p in self._contents:
            if hasattr(p, "comments") and p.comments:
                p.comments.filter_by_ranking(low_limit, high_limit)
                p.comments_count = len(p.comments)
                if p.comments:
                    p.last_comment = p.comments.list()[-1].added

    def filter_by_tags(self, tags):
        tags = Tags(tags)
        if not tags:
            return
        self.annotate_by_tags()  # prereq
        tagset = tags.set()

        self._contents = [p for p in self._contents
             if p.tags.set() & tagset]

    def annotate_by_repr_coordinates(self):
        # prepare point to be shown in representational coordinate system
        [encode_coordinates(p) for p in self._contents]

    def annotate_by_comments(self):
        for p in self._contents:
            p.comments = Comments(by_point=p)
            p.comments_count = len(p.comments)
            if p.comments:
                p.last_comment = p.comments.list()[-1].added
                p.first = p.comments.first_item()
            else:
                p.first = Comment(text="", id=0)

    def annotate_by_comments_indicators(self):
        for p in self._contents:
            if p.comments:
                p.comments_indicators = p.comments.look_for_indicators()
            else:
                p.comments_indicators = Indicators()

    def last_activity(self, default_last_activity=None):
        self.annotate_by_comments()
        last_activity = default_last_activity
        for p in self._contents:
            if last_activity is None:
                last_activity = p.added
            else:
                last_activity = max(last_activity, p.added)
            try:
                last_activity = max(last_activity, p.last_comment)
            except:
                pass
        self.last_active = last_activity
        return last_activity

    def central_point(self, lat=None, lon=None, zoom=None):
        """Makes mean point from all point coordinates"""
        sum_lat = sum_lon = 0.0
        cnt = 0
        for p in self._contents:
            if p.lat != 0.0 and p.lon != 0.0:  # out of extent check!!!
                cnt += 1
                sum_lat += p.lat
                sum_lon += p.lon

        if sum_lat == 0.0:
            return lat, lon, zoom

        c_lat, c_lon = sum_lat/cnt, sum_lon/cnt
        try:
            if geo_support.dist((c_lat, c_lon), (float(lat), float(lon))) > 30000:
                return lat, lon, zoom
        except:
            pass


        maxdist = 100
        for p in self._contents:
            if p.lat != 0.0 and p.lon != 0.0:  # out of extent check!!!
                d = geo_support.dist((c_lat, c_lon), (float(p.lat), float(p.lon)))
                if d > maxdist:
                    maxdist = d
        zoom = geo_support.zoom_from_dist(maxdist)  #!!! function is not generic
        return c_lat, c_lon, zoom

    def item_tags(self):
        """Should be overriden"""
        return database.point_tags()

    def annotate_by_tags(self, sort_method=None):
        """ Example usage:
        .annotate_by_tags(sort_method=Tags.sort_by_namespace)
        """
        point_ids = set([p.id for p in self._contents if not p.has_key("tags")])
        if point_ids:
            ptdict = dict([(point[0], Tags(point[1]))
                for point in 
                    itertools.groupby(self.item_tags(), lambda t: t.location_id)
                        if point[0] in point_ids])
            if sort_method:
                for p in self._contents:
                    if not p.has_key("tags"):
                        p.tags = ptdict.get(p.id, Tags(tags=''))
                        sort_method(p.tags)
            else:
                for p in self._contents:
                    if not p.has_key("tags"):
                        p.tags = ptdict.get(p.id, Tags(tags=''))

    def annotate_by_profiles(self, default={}):
        for p in self._contents:
            p.profile = Entity(database.object_profile(p))
            for (k, v) in default.items():
                p.profile.setdefault(k, v)

    def annotate_by_projects(self):
        for p in self._contents:
            p.projects = Projects(point=p)
            p.projects.sort_by_added()
            p.projects_count = len(p.projects)
            p.first_project = p.projects.first_item()

    def annotate_by_users(self):
        for p in self._contents:
            p.users = Users(by_having_role_in=p)

def decode_tag(tag):
    # !!! needs more attention
    t = (tag.replace("'", "").replace(",", "")      # these to protect SQL
        .replace("\\", "").replace("/", "").replace("+", "") # these to
            # protect UM interface
        .lower()
    )
    return tuple(([""] + t.split(":", 1))[-2:])

def string_to_tags(tag_str):
    return [Tag(ns_tag=":".join(tag), 
                tag=tag[1], 
                tag_namespace=tag[0],
                tag_system_id=None,   #!!! not applicable
                count_locations=1,    #!!! not applicable
                count_users=1,        #!!! not applicable 
            ) for tag in 
    set(map(decode_tag, tag_str.replace('/', ' ').replace('+', ' ').split()))
    - set(map(decode_tag, Tag.STOP_LIST.split()))
           ]


class Tags(Collection):

    INSTRUCTION_NAMESPACES = ("filter", "sort")
    UGLY_TAGS = re.compile("|".join([
        r".*[#].*", 
        r".+=\d+", 
        r"geolat\d+", 
        r"geolong?\d+",
        r"cell.+\d+",
        r"bt[0-9a-fA-F]{12}",
    ]))

    def __init__(self,
                 tags=None,
		 points_only=False,
                 project=None,
                 user=None):
        """
        tags is a tag string, db query result or Tags instance
        """
        if tags is None:
	    if points_only:
                self._contents = [Tag(t) for t in database.tags_of_points()]
            elif project:
                self._contents = [Tag(t) for t in database.tags_of_project_points(project)]
	    else:
                self._contents = [Tag(t) for t in database.tags()]
        elif not tags:
            self._contents = []
        elif isinstance(tags, basestring):
            self._contents = string_to_tags(tags)
        elif isinstance(tags, Tags):
            self._contents = tags.list()[:]    # copy is not efficient, but safer
        elif isinstance(tags, type([])) or hasattr(tags, "next"):
            self._contents = [Tag(t) for t in tags]
        else:                # if tags is None or not Tags:
            self._contents = []
        self._remove_dups()
        self.make_safe()

    def tag_point(self, point, user):
        database.tags_insert(point, user, self, deny_namespaces=[])

    def untag_point(self, point, user):
        database.tags_remove(point, self)

    def append(self, tags):
        self._contents.extend(Tags(tags)._contents)
        self._remove_dups()

    def _remove_dups(self):
        self._contents = dict([(t.ns_tag, t) for t in self._contents]).values()
        self.sort_by_namespace()

    def _prepare_instructions(self, tags):
        instr = {}
        for t in tags:
            tag, value = t.tag, ''
            if "=" in tag:
                tag, value = tag.split("=", 1)
            key = t.tag_namespace + ":" + tag
            instr[key] = value
        return instr
    
    def extract_instructions(self):
        special_tags = [t for t in self._contents
                        if t.tag_namespace in self.INSTRUCTION_NAMESPACES]
        self._contents = [t for t in self._contents
                        if t.tag_namespace not in self.INSTRUCTION_NAMESPACES]

        return self._prepare_instructions(special_tags)

    def make_safe(self):
        # this is HTML view specific method
        res = []
        for q in self._contents:
            q.safetag = q.tag.replace("?", "%3F")
            q.safe_ns_tag = q.ns_tag.replace("?", "%3F")
            q.safe_tag = q.ns_tag.lstrip(":").replace("?", "%3F")
            res.append(q)
        self._contents = res

    def sort_by_namespace(self):
        self._contents.sort(key=lambda x: (x.tag_namespace, x.tag))

    def sort_by_tag(self):
        self._contents.sort(key=lambda x: x.tag)

    def sort_by_count_locations(self):
        self._contents.sort(key=lambda x: x.count_locations, reverse=True)

    def annotate_by_tag_levels(self):
        for t in self._contents:
            t.tag_level = int(math.log(t.count_locations + 3))

    def filter_ugly_tags(self):
        tags = []
        for t in self._contents:
            if not self.UGLY_TAGS.match(t.tag):
                tags.append(t)
        self._contents = tags

    def filter_not_in_namespaces(self, namespaces):
        self._contents = [t for t in self._contents
                            if t.tag_namespace not in namespaces]

    def filter_by_namespaces(self, namespaces):
        self._contents = [t for t in self._contents
                            if t.tag_namespace in namespaces]

    def item_id(self, item):
        return item["ns_tag"]

    def for_str(self):
        return " ".join([x.lstrip(":") for x in self.set()])

class Comments(Collection):

    def __init__(self,
                 id=None,
		 by_point=None,
		 by_user=None,
                 user=None):
        """ If id is given, Comments will contain just one (or zero)
        comments with given id.
        """
        if id == 0:
            self._contents = []
        elif id is not None:
            db_comments = database.comment_by_id(id)
        elif by_point is not None:
            db_comments = database.comments_by_point(by_point)
        elif by_user is not None:
            db_comments = database.comments_by_user(by_user)
        else:
            db_comments = database.comments()
        self._contents = [Comment(c) for c in db_comments]  # if c.text
        #self.filter_by_visibility()

    @staticmethod
    def store(comment, point, user):
        comment.text = util.sanitize_html(comment.text)
        comment.setdefault("type", "comment")
        comment.id = database.comment_insert(comment, point, user)

    @staticmethod
    def update(comment, point, user):
        comment.text = util.sanitize_html(comment.text)
        database.comment_update(comment, point, user)

    def store_order(self):
        for p in self._contents:
            database.comment_order_update(p)

    def sort_by_order(self):
        self._contents.sort(key=lambda x: (-x.ord, x.added), reverse=True)

    def hide(self):
        for p in self._contents:
            database.hide_comment(p)

    def delete(self):
        for p in self._contents:
            database.delete_comment(p)
        self._contents = []

    def filter_by_user(self, user):
        userid = user.id
        self._contents = [p for p in self._contents if p.user_id == userid]

    def filter_by_ranking(self, low_limit=-200, high_limit=200):
        self._contents = [c for c in self._contents if low_limit <= c.ranking <= high_limit]

    def filter_by_visibility(self, state=1):
        self._contents = [p for p in self._contents if p.visible == state]

    def filter_by_type(self, comment_type):
        self._contents = [p for p in self._contents if p.type == comment_type]

    def look_for_indicators(self):
        indicators = Indicators()
        for c in self._contents:
            for url in finditer_urls(c.text):
                if url.startswith("/media"):   # these ifs are the same as in view !!!
                    if "images" not in indicators:
                        indicators.images = [config.base_url + url]
                    else:
                        indicators.images.append(config.base_url + url)
                elif url.startswith("feed:"):
                    if "feeds" not in indicators:
                        indicators.feeds = [url[5:]]   # get rid of prefix
                    else:
                        indicators.feeds.append(url[5:])  # -"-
                elif url.startswith("source:"):
                    if "source" not in indicators:
                        indicators.sources = [url[7:]]   # get rid of prefix
                    else:
                        indicators.sources.append(url[7:])  # -"-
                elif url.startswith("query:"):
                    if "queries" not in indicators:
                        indicators.queries = [url[6:]]   # get rid of prefix
                    else:
                        indicators.queries.append(url[6:])  # -"-
                elif url.lower().startswith(config.base_url.lower().rstrip("/")+"/"):
                    if "internal_urls" not in indicators:
                        indicators.internal_urls = [url]
                    else:
                        indicators.internal_urls.append(url)
                elif not url.startswith("/"):
                    if "urls" not in indicators:
                        indicators.urls = [url]
                    else:
                        indicators.urls.append(url)
        return indicators

    def last_activity(self, default_last_activity=None):
        last_activity = default_last_activity
        for p in self._contents:
            if last_activity is None:
                last_activity = p.added
            else:
                last_activity = max(last_activity, p.added)
        self.last_active = last_activity
        return last_activity

    def annotate_by_profiles(self, default={}):
        for p in self._contents:
            p.profile = Entity(database.note_profile(p))
            for (k, v) in default.items():
                p.profile.setdefault(k, v)

    def annotate_by_points(self):
        for p in self._contents:
            p.points = Points(by_comment=p)

class Users(Collection):

    def __init__(self,
                 id=None,
                 credentials=None,
		 username=None,
                 description=None,
                 by_having_role_in=None):
        # !!! del p.credentials but for the first "if"
        if credentials:
            if "wsse" in credentials:
                username = wsse.auth_reply(credentials.wsse, database.pwd_function)
                del credentials.wsse
                if not username:
                    self._contents = []
                self._contents = user_by_username(username)
            else:
                self._contents = [User(p) 
                    for p in database.check_credentials(credentials)]
        elif id:
            self._contents = user_by_id(id)
        elif username:
            self._contents = user_by_username(username)
        elif by_having_role_in:
            self._contents = [User(u) for u in database.user_by_location_role(by_having_role_in)]
        elif description:
            self._contents = [User(p) 
                for p in database.user_by_description(description)]
        else:
            self._contents = []
        self.annotate_by_groups()

    @staticmethod
    def store(user, profile, group):
        if not hasattr(user, "id"):
            user.setdefault("description", group.groupname)
            database.user_insert(user)
            user = User(user_by_username(user.username)[0])
        else:
            if user.password is not None:
                database.user_update(user)
        if profile is not None:
            database.profile_update(user, profile)
        if group is not None:
            database.group_update(user, group)

    def annotate_by_groups(self):
        for p in self._contents:
            p.groups = Groups(user=p)
            p.groupnames = [n.groupname for n in p.groups]

    def annotate_by_projects(self):
        for p in self._contents:
            p.projects = Projects(by_user=p)
            p.projects.annotate_by_profiles(default=DEFAULT_TOPIC_PROFILE)  #!!! ?
            p.projects.annotate_by_latest_points()

    def annotate_by_points(self):
        for p in self._contents:
            p.points = Points(by_user=p)
            p.points.annotate_by_projects()  #!!! ?
            p.points.annotate_by_profiles(default=DEFAULT_POINT_PROFILE)

    def annotate_by_comments(self):
        for p in self._contents:
            p.comments = Comments(by_user=p)
            # need to know points and topics... !!!

    def annotate_by_profiles(self, default={}):
        for p in self._contents:
            p.profile = Entity(database.user_profile(p))
            for (k, v) in default.items():
                p.profile.setdefault(k, v)


def add_resource_once(url, user, aged=None):
    for point in external_points(urls=[url], aged=aged):
        database.external_point_update(point, user)


POINT_ID_RE = re.compile(config.base_url + "/topic/(?:\d+)/point/(\d+)")
POINT_ID_FORMAT = "\n%s/topic/%s/point/%s"

def media_file_html(media_url):
    media_url = config.base_url + media_url
    return """<a href="%(media_url)s"><img src="%(media_url)s&amp;preview=1" alt="[]" /></a>""" % vars()

def _add_attachments(point, user):
    if "text" in point and point.text:
        comment = Comment(text=point.text, origin=point.origin)
        Comments.store(comment, point, user)
    if "attachments" in point:
        for a in point.attachments:
            try:
                fetch_enclosure(a)   # updates a
                media_url = media.uploadMediaFile(a.content.read(),
                                    filename=a.filename,
                                    content_type=a.content_type,
                                  )
                comment_text = media_file_html(media_url)
            except:
                continue
                #comment_text = "failed loading %s " % a.filename
            comment = Comment(text=comment_text, origin=point.origin)
            Comments.store(comment, point, user)

def _receipt_stamp(point, feed, user):
    comment_text = "source:" + feed.url + " " + feed.description
    comment = Comment(text=comment_text, origin=point.origin)
    Comments.store(comment, point, user)

def _receipt_stamp_if_needed(points, feed, user):
    points.annotate_by_comments()
    points.annotate_by_comments_indicators()
    point = points.first_item()
    try:
        if not (point.comments_indicators 
              and "sources" in point.comment_indicators 
              and point.comment_indicators.sources 
              and feed.url in point.comment_indicators.sources):
            _receipt_stamp(point, feed, user)
    except:
        pass

def add_points_from_feed(project, feed, user, aged=None):
    try:
        aged = aged or int(feed.frequency)
    except:
        aged = 3600*24  #!!!
#    if not need_to_load_ds(feed.url, aged):
#        return
    if feed.type != "autoissuefeed":
        # !!! need to add descriptions!
        for point in external_points(urls=[feed.url], aged=aged):
            result = database.external_point_update(point, user)
            database.update_projects_points(project, point)
            if result == "insert":
                _add_attachments(point, user)

    else:  # do not create new point, add attachment to the old one
        # the below functionality is issue-reporting hack !!!
        # !!! need to add descriptions!
        for point in external_points(urls=[feed.url], aged=aged, origin='official'):
            if not POINT_ID_RE.search(point.description):  # hack!!!
                result = database.external_point_update(point, user)
                database.update_projects_points(project, point)
                if result == "insert":
                    _add_attachments(point, user)                    
                _receipt_stamp_if_needed(Points(id=point.id), feed, user)

            else:
                # look into description for point_id hints
                corr_point_id = None
                for m in POINT_ID_RE.finditer(point.description):
                    if m:
                        corr_point_id = int(m.groups()[0].lstrip("0") or "0")
                corr_points = Points(id=corr_point_id)
                if not corr_points:  # issue possibly originated here but now lost
                    result = database.external_point_update(point, user)
                    database.update_projects_points(project, point)
                    if result == "insert":
                        _add_attachments(point, user)                    
                        _receipt_stamp(point, feed, user)
                else:
                    _receipt_stamp_if_needed(corr_points, feed, user)

class Projects(Points):

    def __init__(self,
                 tags="",
                 id=None,
                 user=None,
                 by_user=None,
                 internal=None,   # dummy
                 external=None,   # dummy
                 point=None,
                 search_query="",
                 properties=None,
                 by_user_role=None,  # tuple (user, role)
                 ds=None):
        """ If id is given, Points will contain just one (or zero)
        points with given id.
        tags is a tag string.
        """
        if id == 0:
            self._contents = []
        elif id is not None:
            self._contents = project_by_id(id)
            self.annotate_by_tags()
            self.annotate_by_comments()
        elif ds is not None:
            self._contents = [Project(p) for p in
                database.projects_by_ds(ds)]
        elif by_user is not None:
            self._contents = [Project(p) for p in
                database.projects_by_user(by_user)]
        elif search_query:
            self._contents = search_projects(search_query)
        elif by_user_role:
            self._contents = [Project(p) for p in
                database.objects_by_user_role(by_user_role[0], by_user_role[1], type="project")
            ]
        else:
            tags = Tags(tags)
            instructions = tags.extract_instructions()
            if point:
                self._contents = internal_projects(tags, point=point) or []
            else:
                self._contents = internal_projects(tags) or []
            if "filter:inappropriate" in instructions:
                self.filter_by_ranking(low_limit=-199, high_limit=-99)
        #self.filter_by_visibility()   # special cases?

    @staticmethod
    def store(point, user):
        point.id = database.project_insert(point, user)
        if getattr(point, "uuid", None):  # uuid for internal point
            point.uuid = "%s" % point.id
            database.project_update(point, user)

    @staticmethod
    def create(user, name, lat, lon, url, origin, tags, category,
               description='',
               attachments=None):

        project = Project(title=name, lat=lat, lon=lon, url=url, origin=origin)
        comment = Comment(text=description, origin=origin, type="comment")
        Projects.store(project, user)
        Comments.store(comment, project, user)

        manual_category = False
        if tags:
            tags = Tags(tags)
            tags.tag_point(project, user)
            # see if user attempted to enter category: manually into tags
            for t in tags:
                if t.tag_namespace == "category":
                    manual_category = True
                    break
        if not (manual_category and category.strip() == "category:"):
            cat_tags = Tags(category.strip())
            cat_tags.tag_point(project, user)
        # else category entered through tags and Uncategorized:
        # no need to tag as Uncategorized.

        if 0:  #!!! not implemented
            check_triggers(project, "addproject", 
                project=project,
                user=user,
            )

        Projects.do_set_roles(project, user, 
            ["subscribed", "manage_users", "manage_project"], user)

        return project

    @staticmethod
    def update(user, project, tags=None):
        database.project_update(project, user)
        if tags is None:
            return project
        # tags are trickier:
        # 1. add tags
        tags_to_add = Tags(" ".join(tags.set() - project.tags.set()))
        tags_to_add.make_safe()
        tags_to_add.tag_point(project, user)
        # 2. remove tags
        tags_to_del = Tags(" ".join(project.tags.set() - tags.set()))
        tags_to_add.make_safe()
        tags_to_del.untag_point(project, user)
        project.tags = tags

        return project

    def annotate_by_datasources(self):
        for p in self._contents:
            p.datasources = Datasources(project_id=p.id)
            p.datasources_count = len(p.datasources)

    def annotate_by_triggers(self):
        for p in self._contents:
            p.triggers = Triggers(project_id=p.id)
            p.triggers_count = len(p.triggers)


    def annotate_by_points(self):
        for p in self._contents:
            p.points = Points(project=p)
            p.points.sort_by_added()
            p.points_count = len(p.points)
            p.latest_point = p.points.first_item()

    def annotate_by_latest_points(self):
        for p in self._contents:
            p.points = Points(project=p, limit=1)
            p.latest_point = p.points.first_item()

    def annotate_by_points_count(self):
        for p in self._contents:
            try:
                p.points_count = list(database.points_count_by_project(p))[0].points_count
            except:
                p.points_count = 0

    def hide(self):
        for p in self._contents:
            database.hide_project(p)

    def item_tags(self):
        """Should be overriden"""
        return database.project_tags()

    def sort_by_points_count(self):
        self._contents.sort(key=lambda x: x.points_count, reverse=True)

    def sort_by_vitality(self):
        """ Vitality to be better defined later"""
        #self.annotate_by_comments()
        self.annotate_by_latest_points()
        now = util.now()
        for p in self._contents:
            last_activity = p.added
            try:
                last_activity = max(last_activity, p.last_comment)
            except:
                pass
            try:
                last_activity = max(last_activity, p.points.first_item().added)
            except:
                pass
            p.vitality = last_activity  #100 / ((now - last_activity).days + 1)
        self._contents.sort(key=lambda x: x.vitality, reverse=True)


    def last_activity(self, default_last_activity=None):
        # !!! very heavy method
        #self.annotate_by_comments()
        self.annotate_by_points()
        last_activity = default_last_activity
        for p in self._contents:
            if last_activity is None:
                last_activity = p.added
            else:
                last_activity = max(last_activity, p.added)
            try:
                last_activity = max(last_activity, p.last_comment)
            except:
                pass
            try:
                last_activity = max(last_activity, p.points.first_item().added)
            except:
                pass
        self.last_active = last_activity
        return last_activity


class Datasources(Collection):

    def __init__(self,
                 id=None,
                 project_id=None,
                 url=None, type_=None,
                 ):
        """ 
        """
        if project_id:
            self._contents = [Datasource(ds) for ds in 
                database.datasources_by_project_id(project_id)]
        elif id:
            self._contents = [Datasource(ds) for ds in 
                database.datasources_by_id(id)]
        elif url and type_:
            self._contents = [Datasource(ds) for ds in 
                database.datasources_by_url_and_type(url, type_)]

    @staticmethod
    def store(datasource, project, user):
        datasource.id = database.datasource_insert(datasource, project, user)

    @staticmethod
    def update(datasource, project, user):
        database.datasource_update(datasource, project, user)

    def delete(self, from_project):
        for p in self._contents:
            database.remove_datasource_from_project(p, from_project)

    def filter_by_type(self, type_):
        self._contents = [p for p in self._contents if p.type == type_]

    def annotate_by_projects(self):
        for p in self._contents:
            p.projects = Projects(ds=p)
            p.projects_count = len(p.projects)


class Categories(Tags):

    def __init__(self,
                 categories=None,
                 user=None):
        """
        """
        self._contents = \
            [Category(t) for t in database.tags_by_namespace(tag_namespace="category")] \
            + [Category(Tags("category:").first_item())]
        self._add_titles()
        self.make_safe()

    def _add_titles(self):
        for p in self._contents:
            if p.tag == "":
                p.title = "Uncategorized"
            else:
                p.title = p.tag.capitalize()

    def annotate_by_projects(self):
        # the code below handles two cases:
        # projects untagged go into uncategorized,
        # others according to category.

        category_tags = self._contents[:-1]
        uncategorized = self._contents[-1]

        categorized_set = set()
        for p in category_tags:
            p.projects = Projects(tags=[p])
            p.projects.sort_by_title()
            p.projects_count = len(p.projects)
            categorized_set |= p.projects.set()

        uncategorized.projects = Projects()

        uncategorized.projects.filter_by_excluding_set(categorized_set)
        uncategorized.projects.sort_by_title()
        uncategorized.projects_count = len(uncategorized.projects)

        if uncategorized.projects_count == 0:
            del self._contents[-1]

        for c in self._contents:
            c.projects.annotate_by_tags()
            c.projects.annotate_by_comments()


class Groups(Collection):

    def __init__(self,
                 groupname=None,
                 user=None,
                 id=None,
                 ):
        """ 
        """
        if id:
            self._contents = [Group(p) for p in 
                database.group_by_id(id)]
        elif groupname:
            self._contents = [Group(p) for p in 
                database.group_by_name(groupname)]
        elif user:
            self._contents = [Group(p) for p in 
                database.groups_by_user(user)]
        else:
            self._contents = [Group(p) for p in 
                database.groups()]


class Triggers(Collection):

    def __init__(self,
                 project_id=None,
                 id=None,
                 condition=None,
                 ):
        """ 
        """
        if id:
            self._contents = [Trigger(p) for p in 
                database.triggers_by_id(id)]
        elif project_id:
            if condition is None:
                self._contents = [Trigger(p) for p in 
                    database.triggers_by_project_id(project_id)]
            else:
                self._contents = [Trigger(p) for p in 
                    database.triggers_by_project_id_with_condition(project_id, condition)]

    @staticmethod
    def store(trigger, project, user):
        trigger.id = database.trigger_insert(trigger, project, user)

    @staticmethod
    def update(trigger, project, user):
        database.trigger_update(trigger, project, user)

    def delete(self):
        for p in self._contents:
            database.delete_trigger(p)
        self._contents = []

def del_by_captcha(captcha):
    database.delete_user_by_description(captcha)

def update_user_description(user, description):
    database.update_user_description(user, description)

def store_message_to_point_and_comments(message, acl_rule):  #!!! should check acl
    """
    input: rfcmessage
    output: point and comment added to the db (if there is location)
    """
    pnt = mail_parser.point_from_message(message)

    if not pnt.lat:
        pnt.lat = config.center_lat
        pnt.lon = config.center_lon

    if pnt.lat:  #!!! is it good antispam measure to allow only location-aware messages?

        user_id = config.default_user_id_for_mail
        user_is_default = True
        try:
            user_id = list(database.search_profile_email(pnt.author))[0].user_id
            user_is_default = False
        except:
            pass

        user = User(id=user_id)

        try:
            # check if point already exists
            pnt1 = list(database.point_by_uuid(pnt.uuid))[0]
            return pnt1
        except:
            pass

        pnt.tags = Tags(pnt.tags)
        pnt.url = ''
        pnt.id = 0
        pnt.ranking = 1
        pnt.distance = 0
        pnt.last_comment = ''
        pnt.origin = 'mail'
        pnt.comments_count = len(pnt.attachments)
        pnt.type = 'point'
        pnt.visible = 1

        # Points.store(pnt, user)   #!!!

        try:
            project_id = pnt._recepients[0]["board_id"]
            projects = Projects(id=int(project_id))
            project = projects.first_item()

            # access rights check
            if user_is_default:
                if not acl_rule(project, None):
                    return
            else:
                if not acl_rule(project, user):
                    return

            Points.store(pnt, user, project)    
        except:
            #raise
            return  # no points without a project
            project_id = None

        comments = []

        comment = Comment(text=' ', origin=pnt.origin)
        first_text = None
        for a in pnt.attachments:
            if a.content_type.startswith("text/plain"):
                text_content = a.content  # !!! drop sig
                if first_text is None:
                    first_text = text_content
                text_content = text_content.split("-- \n", 1)[0]
                comment.text = comment.text + "\n".join([("<p>" + l + "</p>") for l in text_content.split("\n")])
            elif a.content_type.startswith("image/"):
                try:
                    media_url = media.uploadMediaFile(a.content,
                                                      content_type=a.content_type)
                    comment.text += media_file_html(media_url)
                except:
                    pass

        tags = Tags(" ".join(first_text.strip()
                             .replace(",", " ").replace(":", " ").split("\n")[:2]))
        tags.tag_point(pnt, user)
        pnt.tags.tag_point(pnt, user)

        Comments.store(comment, pnt, user)

        return Point(pnt)


def store_attachment(obj_id, user,
                     attach_type='any',
                     origin='', 
                     commenttext='', 
                     url='', 
                     url_title='', 
                     fileinfo={},
                     comment=None):
    try:
        obj = object_by_id_hard(obj_id)[0]
    except:
        return {'message': "ERROR: object not found."}

    if attach_type in ("any", "text", "widget"):
        commenttext = commenttext
    else:
        commenttext = ''

    if comment is None:    
        comment = Comment(text=commenttext, origin=origin)
    else:
        comment.text = commenttext
        comment.origin = origin

    if attach_type == "widget":
        comment.type = "widget"
    else:
        comment.type = "comment"

    if attach_type in ("any", "file"):    
        try:
            fc = fileinfo.file.read()
            if fc:
                media_url = media.uploadMediaFile(fc,
                                  filename=fileinfo.filename)
                comment.text += media_file_html(media_url)
        except:
            pass

    if attach_type in ("any", "link"):
        if url != 'http://' and url.strip():
            comment.text =  comment.text + \
                """<a href="%(url)s">%(url_title)s</a>""" % vars()

    if not comment.text:  # otherwise comment is invisible
        comment.text = "&nbsp;"

    if "id" in comment:
        Comments.update(comment, obj, user)
    else:
        Comments.store(comment, obj, user)
    return {}


def object_by_note(note):
    return database.object_by_note(note.id)


def check_triggers(project, condition, **params):
    for t in Triggers(project_id=project.id, condition=condition):
        triggers.fire_trigger(project, t, **params)  #???

#!!! this is same as in the view
URL_RE = re.compile("((?:feed:|source:)?(?:(?:http|ftp|https|query)://|/)\S*)")

def finditer_urls(text):
    for m in URL_RE.finditer(text):
        yield m.groups()[0]

# those roles could be used for a project
ROLES = ["manage_users", "manage_project", "subscribed"]

def set_object_property(object, profile):
    database.object_profile_update(object, profile)


# universal conversions

def geo_decode(*xy):
    if config.srsname.lower() == "epsg:4326":
        return xy
    if config.use_pyproj and geo_support.coord_conversions:
        return geo_support.coord_decode(xy[0], xy[1], srsname=config.srsname)
    else:
        from plugins import geo
        return geo.decode(*xy)

def geo_encode(*xy):
    if config.srsname.lower() == "epsg:4326":
        return xy
    if config.use_pyproj and geo_support.coord_conversions:
        try:
            return geo_support.coord_encode(xy[0], xy[1], srsname=config.srsname)
        except:
            return 0.0, 0.0
    else:
        from plugins import geo
        return geo.encode(*xy)


def decode_coordinates(obj):
    obj.lat, obj.lon = geo_decode(obj.repr_lat, obj.repr_lon)

def encode_coordinates(obj):
    obj.repr_lat, obj.repr_lon = geo_encode(obj.lat, obj.lon)

def encode_bbox(lo1, la1, lo2, la2):
    p1 = geo_encode(la1, lo1)
    p2 = geo_encode(la2, lo2)
    return (p1[1], p1[0], p2[1], p2[0])

# helper functions to get reasonably annotated objects
# by id. Intended for use from controller.
def t_helper(topic_id):
    topics = Projects(id=int(topic_id))
    topics.annotate_by_profiles(default=DEFAULT_TOPIC_PROFILE)
    if not topics:
        return topics, None
    topic = topics.first_item()
    if not topic:
        raise ValueError, "No such topic"

    return topics, topic

def t_p_helper(topic_id, point_id):
    topics, topic = t_helper(topic_id)

    points = Points(id=int(point_id))
    if not points:
        return topics, topic, points, None

    points.annotate_by_profiles(default=DEFAULT_POINT_PROFILE)
    points.annotate_by_tags()
    points.annotate_by_projects()
    point = points.first_item()

    #: check that the point really belongs to the topic
    if topic.id not in [t.id for t in point.projects]:
        return topics, topic, Points(id=0), None

    return topics, topic, points, point

def t_p_c_helper(topic_id, point_id, comment_id):
    topics, topic, points, point = t_p_helper(topic_id, point_id) 

    comments = Comments(id=int(comment_id))
    if not comments:
        return topics, topic, points, point, comments, None

    comment = comments.first_item()

    comments.annotate_by_points()
    
    #: check that the comment really belongs to the point
    if point.id not in [p.id for p in comment.points]:
        return topics, topic, points, point, Comments(id=0), None

    return topics, topic, points, point, comments, comment

def t_c_helper(topic_id, comment_id):
    topics, topic = t_helper(topic_id) 

    topics.annotate_by_comments()
    for c in topic.comments:
        if int(c.id) == int(comment_id):
            comments = Comments(id=int(comment_id))
            comment = comments.first_item()
            return topics, topic, comments, comment

    return topics, topic, Comments(id=0), None

def t_d_helper(topic_id, ds_id):
    topics, topic = t_helper(topic_id)

    dss = Datasources(id=int(ds_id))
    if not dss:
        return topics, topic, dss, None

    ds = dss.first_item()

    #: check that the datasource really belongs to the topic
    if ds.id not in [p.id for p in Datasources(project_id=topic.id)]:
        return topics, topic, Datasources(id=0), None

    return topics, topic, dss, ds

def t_tr_helper(topic_id, trigger_id):
    topics, topic = t_helper(topic_id)

    triggers = Triggers(id=int(trigger_id))
    if not triggers:
        return topics, topic, triggers, None

    trigger = triggers.first_item()

    #: check that the datasource really belongs to the topic
    if trigger.id not in [p.id for p in Triggers(project_id=topic.id)]:
        return topics, topic, Triggers(id=0), None

    return topics, topic, triggers, trigger

def search_helper(i, topic=None):
    # sanitazing?!!!
    if i.search:
        if i.search_tags:
            properties = Storage(lat=None, lon=None, radius=None)
            return Points(tags=i.search, project=topic,
                        external=True, properties=properties)
        else:
            return Points(project=topic, search_query=i.search, external=None)
    else:
        if "search_nearby" in i and i.search_nearby \
                and i.lat and i.lon:
            lat, lon = float(i.lat), float(i.lon)
            points = Points(
                nearby=(lat, lon, i.nearby_radius, i.get("limit", None)),
                project=topic,
            )
            points.annotate_by_distance(lat, lon)
            points.sort_by_distance()
            return points
        else:
            return Points(project=topic)  # null search

def tags_helper(topic=None):
    """ Prepare tags for the tag cloud """
    tags = Tags(project=topic)
    tags.filter_ugly_tags()
    tags.sort_by_count_locations()
    tags.annotate_by_tag_levels()
    tags.limit_by(config.max_tags)
    tags.sort_by_tag()
    return tags


def order_helper(objects, order, **kwargs):
    """ Apply given order pseudo-inplace """
    if order == "oldest":
        objects.sort_by_added()  #!!!
        objects.reverse()
    elif order == "newest":
        objects.sort_by_added()  #!!!
    elif order == "title":
        objects.sort_by_title()
    elif order == "most points":
        objects.sort_by_points_count()
    elif order == "recently updated":
        objects.sort_by_vitality()
    elif order == "distance":
        objects.sort_by_distance()
    elif order == "most comments":
        objects.annotate_by_comments_count()
        objects.sort_by_comments_count()


def geocoding_example():
    real_geocoding_example = geocoding.example()
    if real_geocoding_example:
        return real_geocoding_example

    geo_lookup = Projects(tags=Tags("official:geocoding_source"))
    geo_lookup.annotate_by_points()

    for t in geo_lookup:
        for p in t.points:
            return p.title.lower()

    return ''

def geocoding_helper(address, onfail=(0.0, 0.0), metadata=None):
    # 1. standard geocoding
    res = Storage()
    if not address:
        res.lat, res.lon = onfail
        res.geocoding = "failed"
        res.address = ''
        res.example = geocoding.example()
        return res
    try:
        if config.srsname in geocoding.supported_srs:
            res.repr_lat, res.repr_lon, metadata1 = \
                geocoding.street_latlon(address=address, 
                                        srs=config.srsname,
                                        metadata=metadata)
            decode_coordinates(res)
            if "zoom" in metadata1:
                res.zoom = metadata1["zoom"]
        elif "EPSG:4326" in geocoding.supported_srs:
            res.lat, res.lon, metadata1 = \
                geocoding.street_latlon(address=address, metadata=metadata)
            encode_coordinates(res)
            if "zoom" in metadata1:
                res.zoom = metadata1["zoom"]
        else:
            res = Storage()
    except:
        res = Storage()
    if res:
        res.geocoding = "successful"
        res.address = address
        res.example = geocoding.example()
        return res
    
    # 2. folksonomy-style geocoding
    geo_lookup = Projects(tags=Tags("official:geocoding_source"))
    geo_lookup.annotate_by_points()

    # !!! INEFFICIENT
    for t in geo_lookup:
        for p in t.points:
            if p.title.lower() == address.lower().strip():
                res.lat = p.lat
                res.lon = p.lon
                break 
    if res:
        res.geocoding = "successful"
        res.address = address
        res.example = geocoding.example()
        encode_coordinates(res)
        return res

    # everything fails
    res.lat, res.lon = onfail
    res.geocoding = "failed"
    res.address = address
    res.example = geocoding.example()
    return res

def enable_point_by_id(point_id, topic, user):
    point = point_by_id_hard(point_id)
    database.enable_point_by_id(point_id, user)
    database.replace_and_delete_user(point[0].user_id, user.id)

    check_triggers(topic, "addpoint", 
        point=point,
        user=user,
    )

def doc_helper(context, doc_name, language):
        doc_key = "doc_" + doc_name
        try:
            doc_dict = getattr(config, doc_key)
        except:
            doc_dict = None
            own_content = ""   # not configured

        file_key = ""
        try:
            if doc_dict:
                file_key = doc_dict[language]
                own_content = media.file_storage.getItem(file_key, mode="str")
            else:
                file_key = ""
        except:
            try:
                file_key = doc_dict["en"]
                own_content = media.file_storage.getItem(file_key, mode="str")
            except:
                file_key = ""
                own_content = ""   # not configured ?

        context.update(
            doc_key=doc_key,
            doc_language=language,
            file_key=file_key,
        )
        return own_content
