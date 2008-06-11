# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Module for database queries. Used mostly by model.py
    but also for low-level things in code.py
"""

import web
import config
import re
import datetime
import geo_support

def LOCATIONS_GROUP_BY(tbl="locations"):
    return ", ".join([tbl + "." + fld for fld in 
      """id lat lon title added user_id origin ranking url uuid begins expires ends visible type""".split()])

TAGS_GROUP_BY = """tags.id, tags.tag, tags.tag_namespace, tag_namespaces.tag_system_id"""

USERS_GROUP_BY = """users.id, users.username, users.added, users.description"""

BASE_LOCATIONS_QUERY = """
    SELECT locations.*, 
       0 as distance, 
       MAX(notes.added) as last_comment, 
       COUNT(DISTINCT(notes.id)) as comments_count,
       COUNT(DISTINCT(projects_points.location_id)) as points_count,
       users.username as author
    FROM locations
    LEFT JOIN users ON (locations.user_id = users.id)
    LEFT JOIN notes ON (notes.visible = 1 AND notes.location_id = locations.id)
    LEFT JOIN projects_points ON (projects_points.project_id = locations.id and projects_points.visible = 1)
    """

BASE_PROJECTS_QUERY = """
    SELECT locations.*, 
       0 as distance, 
       MAX(notes.added) as last_comment, 
       COUNT(DISTINCT(notes.id)) as comments_count,
       users.username as author
    FROM locations
    LEFT JOIN users ON (locations.user_id = users.id)
    LEFT JOIN notes ON (notes.location_id = locations.id)
    """


def object_by_(cond, **query):
    """This may be obsoleted anytime """
    qry = (BASE_LOCATIONS_QUERY 
        + """WHERE locations.visible = 1 AND """ + cond + """
        GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
        LIMIT 1;
        """)
    return web.query(qry, vars=query)

def object_by_hard_(cond, **query):
    """This may be obsoleted anytime """
    qry = (BASE_LOCATIONS_QUERY 
        + """WHERE """ + cond + """
        GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
        LIMIT 1;
        """)
    return web.query(qry, vars=query)

def object_by_id(id):
    return object_by_("""locations.id = $id""", id=id)

def object_by_id_hard(id):
    return object_by_hard_("""locations.id = $id""", id=id)

def point_by_id(id):
    return object_by_("""locations.id = $id 
                         AND locations.type = 'point'""", id=id)

def point_by_id_hard(id):
    """ hard means - also invisible """
    return object_by_hard_("""locations.id = $id 
                         AND locations.type = 'point'""", id=id)

def object_by_note(note_id):
    return object_by_("""notes.id = $note_id 
                      """, note_id=note_id)

def point_by_uuid(uuid):
    return object_by_("""locations.uuid = $uuid 
                  AND locations.type = 'point'""", uuid=uuid)

def project_by_id(id):
    return object_by_("""locations.id = $id 
                         AND locations.type = 'project'""", id=id)

def comments():
    return web.query("""
        SELECT n.*, l.lat as lat, l.lon as lon, l.id as location_id, l.title as location_title, u.username as author
        FROM notes n, locations l, users u
        WHERE l.visible = 1 AND n.visible = 1 
            AND n.location_id = l.id
            AND n.user_id = u.id
            AND l.type = 'point'
        ORDER BY added DESC;
    """)


def comment_by_id(id):
    return web.query("""
        SELECT n.*, 
	       l.lat as lat, 
	       l.lon as lon, 
	       l.id as location_id, 
	       l.title as location_title, 
	       u.username as author
        FROM notes n, locations l, users u
        WHERE l.visible = 1 AND n.visible = 1 
            AND n.location_id = l.id 
            AND n.user_id = u.id
--            AND l.type = 'point'
            AND n.id = $comment_id
        LIMIT 1;
    """, vars=dict(comment_id=id))

def comments_by_point(point):
    return web.query("""
        SELECT n.*, l.lat as lat, l.lon as lon, l.id as location_id, 
               l.title as location_title, u.username as author
        FROM notes n, locations l, users u
        WHERE l.visible = 1 AND n.visible = 1 
            AND n.location_id = $point_id 
            AND n.location_id = l.id 
            AND n.user_id = u.id
--            AND l.type = 'point'
        ORDER BY n.ord, n.added;
    """, vars=dict(point_id=point.id))

def comments_by_user(user):
    return web.query("""
        SELECT n.*, l.lat as lat, l.lon as lon, l.id as location_id, 
               l.title as location_title, $username as author
        FROM notes n, locations l
        WHERE l.visible = 1 AND n.visible = 1 
            AND n.user_id = $user_id
            AND n.location_id = l.id
            AND n.origin = $origin
            AND l.type = 'point'
        ORDER BY added DESC;
    """, vars=dict(user_id=user.id, username=user.username, origin=config.origin))



def point_insert(point, user, times=[]):
    return web.insert("locations", 
                      lat=point.lat, 
		      lon=point.lon, 
		      title=point.title, 
                      user_id=user.id, 
		      origin=point.origin,
		      url=point.url,
                      visible=point.visible,
                      # added=datetime.datetime.utcnow(),  #!!!
                      uuid=point.get("uuid", ''))

def project_insert(project, user):
    return web.insert("locations", 
                      lat=project.lat,    #!!!
		      lon=project.lon,    #!!!
		      title=project.title, 
                      user_id=user.id, 
		      origin=project.origin,
                      type='project',
		      url=project.url)

def trigger_insert(trigger, project, user):
    return web.insert("triggers", 
                      trigger_condition=trigger.trigger_condition,
                      trigger_action=trigger.trigger_action,
                      adapter=trigger.adapter,
                      url=trigger.url,
                      description=trigger.description,
                      user_id=user.id, 
		      project_id=project.id,
                      )

def trigger_update(trigger, project, user):
    return web.update("triggers", where='id=$id', 
                      trigger_condition=trigger.trigger_condition,
                      trigger_action=trigger.trigger_action,
                      adapter=trigger.adapter,
                      url=trigger.url,
                      description=trigger.description,
                      user_id=user.id, 
		      project_id=project.id,
                      vars={'id': trigger.id},
                      )

def comment_insert(comment, point, user):
    if comment.get("text", ""):
        return web.insert("notes", 
                        text=comment.text,
	                location_id=point.id,
		        user_id=user.id,
		        origin=comment.origin,
                        ranking=0,
                        type=comment.type,
                        )

def comment_update(comment, point, user):
    return web.update("notes", where='id=$id', 
                        text=comment.text,
#	                 location_id=point.id,
#		         user_id=user.id,
#		         origin=comment.origin,
                        type=comment.get("type", "comment"),
#                        ranking=0,
                        vars={'id': comment.id},
                        )

def comment_order_update(comment):
    return web.update("notes", where='id=$id', 
                        ord=comment.ord,
                        vars={'id': comment.id,},
                        )


def _has_tags(tag_list):
    """ Forms a condition to check for certain tags """
    query_str = ""
    for tag_namespace, tag in tag_list:
        anded = "(tags.tag_namespace = " + web.sqlquote(tag_namespace) + \
            " AND " + "tags.tag = " + web.sqlquote(tag) + ")"
        query_str += (query_str and (" OR " + anded) or anded)

    return query_str and ("(" + query_str + ")") or query_str


WORDCHARS = re.compile(r'["\n'+r"'\[\]><\\;\*\?\+]")   #!!! better escape

if web.config.db_parameters["dbn"] == "mysql":
    REGEXQ = """ %s REGEXP %s """
else:
    REGEXQ = """ %s ~ %s """

def _has_query_str(fieldname, qs):
    query_str = ""
    for q in [WORDCHARS.sub('', c.strip()) for c in qs.split()]:
        qq = '[[:<:]]%s[[:>:]]' % q
        cond = REGEXQ % (fieldname, web.sqlquote(qq))
        query_str += query_str and (" OR " + cond) or cond
    return query_str

def search_locations(search_query, tag_list, loctype='point'):

    conds1 = "(" + " OR ".join(
        ["(" + _has_query_str(fieldname, search_query) + ")"
            for fieldname in ("title", )]) + ")"

    select1 = """(SELECT id, 2 as weight FROM locations
        WHERE type = """ + web.sqlquote(loctype) + """
            AND """ + conds1 + """)"""

    conds2 = "(" + " OR ".join(
        ["(" + _has_query_str(fieldname, search_query) + ")"
            for fieldname in ("text", )]) + ")"

    select2 = """(SELECT location_id as id, 2 as weight FROM notes
        WHERE """ + conds2 + """)"""

    select3 = """(SELECT locations_users_tags.location_id as id, 
                         4 as weight
            FROM tags, locations_users_tags
            WHERE  """ + _has_tags(tag_list) + """
                AND locations_users_tags.tag_id = tags.id
            )"""

    selects = (""
            + select1
            + "\nUNION " 
            + select2
            + "\nUNION "
            + select3
            )


    wq = """
        SELECT locations.*, 
            locids.weight, 
            0 as distance, 
            MAX(notes.added) as last_comment, 
            COUNT(notes.location_id) as comments_count,
            users.username as author
        FROM (""" + selects + """) AS locids
        LEFT JOIN locations ON (locations.id = locids.id)
        LEFT JOIN notes ON (notes.visible = 1 AND notes.location_id = locids.id)
        LEFT JOIN users ON (users.id = locations.user_id)
        WHERE
            locations.visible = 1 
            AND locations.type = """ + web.sqlquote(loctype) + """
        GROUP BY """ + LOCATIONS_GROUP_BY('locations') + """, locids.weight, users.username
        ORDER BY locids.weight DESC, last_comment DESC
    ;"""

    return web.query(wq)

def search_locations_of_project(search_query, tag_list, project=None, loctype='point'):

    project_id = project.id

    conds1 = "(" + " OR ".join(
        ["(" + _has_query_str(fieldname, search_query) + ")"
            for fieldname in ("title", )]) + ")"

    select1 = """(SELECT id, 2 as weight FROM locations
        WHERE type = """ + web.sqlquote(loctype) + """
            AND """ + conds1 + """)"""

    conds2 = "(" + " OR ".join(
        ["(" + _has_query_str(fieldname, search_query) + ")"
            for fieldname in ("text", )]) + ")"

    select2 = """(SELECT location_id as id, 2 as weight FROM notes
        WHERE """ + conds2 + """)"""

    select3 = """(SELECT locations_users_tags.location_id as id, 
                         4 as weight
            FROM tags, locations_users_tags
            WHERE  """ + _has_tags(tag_list) + """
                AND locations_users_tags.tag_id = tags.id
            )"""

    selects = (""
            + select1
            + "\nUNION " 
            + select2
            + "\nUNION "
            + select3
            )


    wq = """
        SELECT locations.*, 
            locids.weight, 
            0 as distance, 
            MAX(notes.added) as last_comment, 
            COUNT(notes.location_id) as comments_count,
            users.username as author
        FROM (""" + selects + """) AS locids
        LEFT JOIN locations ON (locations.id = locids.id)
        LEFT JOIN projects_points as pp ON 
            (pp.location_id = locations.id AND pp.visible = 1)
        LEFT JOIN notes ON (notes.visible = 1 AND notes.location_id = locids.id)
        LEFT JOIN users ON (users.id = locations.user_id)
        WHERE
            locations.visible = 1 
            AND pp.project_id = """ + str(int(project_id)) + """
            AND locations.type = """ + web.sqlquote(loctype) + """
        GROUP BY """ + LOCATIONS_GROUP_BY('locations') + """, locids.weight, users.username
        ORDER BY locids.weight DESC, last_comment DESC
    ;"""

    return web.query(wq)


def points_by_tags(tag_list):
    # union!!!
    if not tag_list:
        raise "invalid arguments"

    return web.query("""
        SELECT locations.*
            FROM 
              ( """ + BASE_LOCATIONS_QUERY + """
                WHERE locations.visible = 1 
                    AND locations.type = 'point'
                GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
                ORDER BY last_comment DESC
              ) as locations, 
              tags, locations_users_tags
            WHERE 
                locations_users_tags.location_id = locations.id
                AND """ + _has_tags(tag_list) + """
                AND locations_users_tags.tag_id = tags.id
            GROUP BY """ + LOCATIONS_GROUP_BY() + """, 
                locations.distance, locations.last_comment, 
                locations.comments_count, locations.author, locations.points_count
    """)

def points_by_project_and_tags(project, tag_list):
    # union!!!
    if not tag_list:
        raise "invalid arguments"

    project_id = project.id

    return web.query("""
        SELECT locations.*
            FROM 
              ( """ + BASE_LOCATIONS_QUERY + """
                LEFT JOIN projects_points as pp ON 
                       (pp.location_id = locations.id AND pp.visible = 1)
                WHERE locations.visible = 1
                    AND locations.type = 'point'
                    AND pp.project_id = """ + str(int(project_id)) + """
                GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
                ORDER BY last_comment DESC
              ) as locations, 
              tags, locations_users_tags
            WHERE locations_users_tags.location_id = locations.id
                AND """ + _has_tags(tag_list) + """
                AND locations_users_tags.tag_id = tags.id
            GROUP BY """ + LOCATIONS_GROUP_BY() + """, 
                locations.distance, locations.last_comment, 
                locations.comments_count, locations.author, locations.points_count
    """, vars=dict(project_id=project_id))

def projects_by_tags(tag_list):
    # union!!!
    if not tag_list:
        raise "invalid arguments"

    q = ("""
        SELECT locations.*
            FROM 
              ( """ + BASE_LOCATIONS_QUERY + """
                WHERE locations.visible = 1
                    AND locations.type = 'project'
                GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
                ORDER BY last_comment DESC
              ) as locations, 
              tags, locations_users_tags
            WHERE locations_users_tags.location_id = locations.id
                AND """ + _has_tags(tag_list) + """
                AND locations_users_tags.tag_id = tags.id
            GROUP BY """ + LOCATIONS_GROUP_BY() + """, 
                locations.distance, locations.last_comment, 
                locations.comments_count, locations.author, locations.points_count
    """)
    return web.query(q)

def projects_by_point_and_tags(point, tag_list):
    # union!!!
    if not tag_list:
        raise "invalid arguments"
    
    point_id = point.id

    return web.query("""
        SELECT locations.*
            FROM 
              ( """ + BASE_PROJECTS_QUERY + """
                LEFT JOIN projects_points as pp ON 
                       (pp.project_id = locations.id AND pp.visible = 1)
                WHERE locations.visible = 1
                    AND locations.type = 'project'
                    AND pp.location_id = $point_id
                GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
                ORDER BY last_comment DESC
              ) as locations, 
              tags, locations_users_tags
            WHERE locations_users_tags.location_id = locations.id
                AND """ + _has_tags(tag_list) + """
                AND locations_users_tags.tag_id = tags.id
            GROUP BY """ + LOCATIONS_GROUP_BY() + """
    """, vars=dict(point_id=point_id))

def points():
    qry = BASE_LOCATIONS_QUERY + """
        WHERE locations.visible = 1
            AND locations.type = 'point'
        GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
        ORDER BY last_comment DESC;
    """
    return web.query(qry)

def points_nearby(lat, lon, radius=None, limit=None, project=None):
    limit = limit and ("LIMIT %i" % limit) or ""
    radius_cond = radius and (""" AND sqrt(pow($lat - lat, 2) * $y + pow($lon - lon, 2) * $x) < $r """) or ""
    x, y = geo_support.meters_per_deg(lat, lon)
    if project:
        project_id = project.id
        qry = BASE_PROJECTS_QUERY + """
            LEFT JOIN projects_points ON 
               (projects_points.location_id = locations.id AND projects_points.visible = 1)
            WHERE locations.visible = 1
                AND locations.type = 'point'
                """ + radius_cond + """
                AND projects_points.project_id = """ + str(int(project_id)) + """
            GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
            ORDER BY last_comment DESC
        """ + limit
    else:
        qry = BASE_LOCATIONS_QUERY + """
            WHERE locations.visible = 1
                AND locations.type = 'point'
                """ + radius_cond + """
            GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
            ORDER BY last_comment DESC
        """ + limit
    return web.query(qry, vars=dict(x=x**2, y=y**2, r=radius, lat=lat, lon=lon))

def projects():
    q = BASE_LOCATIONS_QUERY + """
        WHERE locations.visible = 1
            AND locations.type = 'project'
        GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
        ORDER BY last_comment DESC;
    """
    return web.query(q)

def projects_by_point(point):
    point_id = point.id
    return web.query(BASE_PROJECTS_QUERY + """
        LEFT JOIN projects_points ON 
               (projects_points.project_id = locations.id 
                AND projects_points.visible = 1)
        WHERE locations.visible = 1
            AND locations.type = 'project'
            AND projects_points.location_id = $point_id
        GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
        ORDER BY last_comment DESC
        ;""", vars=dict(point_id=point_id))

def projects_by_ds(ds):  #!!!
    ds_id = ds.id
    return web.query(BASE_LOCATIONS_QUERY + """
        LEFT JOIN locations_datasources ON 
               (locations_datasources.location_id = locations.id)
        WHERE locations.visible = 1
            AND locations.type = 'project'
            AND locations_datasources.datasource_id = $ds_id
        GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
        ORDER BY last_comment DESC
        ;""", vars=dict(ds_id=ds_id))

def projects_by_user(user):
    user_id = user.id
    return web.query(BASE_LOCATIONS_QUERY + """
        LEFT JOIN locations_datasources ON 
               (locations_datasources.location_id = locations.id)
        WHERE locations.visible = 1
            AND locations.type = 'project'
            AND users.id = $user_id
        GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
        ORDER BY last_comment DESC
        ;""", vars=dict(user_id=user_id))

def points_by_user(user):
    user_id = user.id
    return web.query(BASE_LOCATIONS_QUERY + """
        LEFT JOIN locations_datasources ON 
               (locations_datasources.location_id = locations.id)
        WHERE locations.visible = 1
            AND locations.type = 'point'
            AND users.id = $user_id
        GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
        ORDER BY last_comment DESC
        ;""", vars=dict(user_id=user_id))

def objects_by_user_role(user, role, type="project"):
    user_id = user.id
    return web.query(BASE_LOCATIONS_QUERY + """
        LEFT JOIN locations_policy_table ON 
               (locations_policy_table.user_id = $user_id
                AND locations_policy_table.location_id = locations.id)
        WHERE locations.visible = 1
            AND locations.type = $type
            AND locations_policy_table.role = $role
        GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
        ORDER BY last_comment DESC
        ;""", vars=dict(user_id=user_id, role=role, type=type))


def points_by_comment(comment):
    comment_id = comment.id
    q = BASE_LOCATIONS_QUERY + """
        LEFT JOIN locations_datasources ON 
               (locations_datasources.location_id = locations.id)
        WHERE locations.visible = 1
            AND locations.type = 'point'
            AND notes.id = $comment_id
        GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
        ORDER BY last_comment DESC
        ;"""
    return web.query(q, vars=dict(comment_id=comment_id))

def point_tags():
    # !!! experimental
    # to be searchable, tag_namespace should have tag_namespace!
    return web.query("""
        SELECT locations_users_tags.location_id as location_id,
               tags.id as id,
               CONCAT(tags.tag_namespace, ':', tags.tag) as ns_tag,
               tags.tag as tag,
               tag_namespaces.id as tag_namespace,
               tag_namespaces.tag_system_id as tag_system_id,
               locations_users_tags.location_id as location_id,
               users.username as username
            FROM tags, tag_namespaces, locations_users_tags, users
            WHERE locations_users_tags.tag_id = tags.id
                AND tags.tag_namespace = tag_namespaces.id
                AND locations_users_tags.user_id = users.id
            ORDER BY locations_users_tags.location_id
        ;
    """, vars=locals())

def project_tags():
    # !!! experimental
    return web.query("""
        SELECT locations_users_tags.location_id as location_id,
               tags.id as id,
               CONCAT(tags.tag_namespace, ':', tags.tag) as ns_tag,
               tags.tag as tag,
               tag_namespaces.id as tag_namespace,
               tag_namespaces.tag_system_id as tag_system_id,
               locations_users_tags.location_id as location_id,
               users.username as username
            FROM tags, tag_namespaces, locations_users_tags, users
            WHERE locations_users_tags.tag_id = tags.id
                AND tags.tag_namespace = tag_namespaces.id
                AND locations_users_tags.user_id = users.id
            ORDER BY locations_users_tags.location_id
        ;
    """, vars=locals())


def user_by_id(id):
    return web.select("users", where="id=$id", vars=dict(id=id))

def user_by_username(username):
    return web.select("users", where="upper(username)=upper($username)", 
                        vars=dict(username=username))

def tags_remove(point, tags):
    for tag in tags:
        tag_data = dict(point_id=point.id, 
                        tag=tag.tag, 
                        tag_namespace=tag.tag_namespace)
        web.query("""
            DELETE FROM locations_users_tags 
            USING locations_users_tags, tags
            WHERE tags.id = locations_users_tags.tag_id 
                AND location_id = $point_id
                AND tags.tag = $tag 
                AND tags.tag_namespace = $tag_namespace;
        """, vars=tag_data)

def tags_insert(point, user, tags, deny_namespaces=[]):
    for tag in tags:
        if tag.tag_namespace in deny_namespaces:
            continue  #!!! logic could be: drop namespace or make ns:tag...
        existing_tags = web.query("""
            SELECT id, tag, tag_namespace FROM tags 
                WHERE tag = $tag AND tag_namespace = $tag_namespace;
        """, vars=tag.copy())
        if not existing_tags:
            web.query("""
                INSERT INTO tags (tag, tag_namespace) 
                    VALUES ($tag, $tag_namespace);
            """, vars=tag.copy())
            existing_tags = web.query("""
                SELECT id, tag, tag_namespace FROM tags 
                    WHERE tag = $tag AND tag_namespace = $tag_namespace;
            """, vars=tag.copy())
        assert len(existing_tags) == 1
        tag_id = existing_tags[0].id

        tag_triad = dict(point_id=point.id, user_id=user.id, tag_id=tag_id)

        already_tagged = web.query("""
            SELECT location_id, user_id, tag_id FROM locations_users_tags
                WHERE location_id = $point_id
                AND user_id = $user_id
                AND tag_id = $tag_id;
        """, vars=tag_triad)

        if not already_tagged:
            web.query("""
            INSERT INTO locations_users_tags (location_id, user_id, tag_id) 
                VALUES ($point_id, $user_id, $tag_id);
            """, vars=tag_triad)

def update_projects_points(project, point):
    project_id = project.id

    if not hasattr(point, "id"):
        db_point = list(point_by_uuid(point.uuid))
        if db_point:
            # !!! should we update lat, lon too?
            point_id = db_point[0].id
        else:
            point_id = 0   #!!!
    else:
        point_id = point.id

    exists = web.query("""
        SELECT * FROM projects_points
            WHERE 
                location_id=$point_id 
                AND project_id=$project_id
                AND projects_points.visible = 1
            LIMIT 1;
            """, vars=locals())

    if not exists:
        web.insert("projects_points", 
                  location_id=point_id, 
		  project_id=project_id,
                  visible=project.visible and getattr(point, "visible", 1),
                  )

def points_by_project(project, limit=None):
    project_id = project.id
    if limit:
        limit = "LIMIT %i" % limit
    else:
        limit = ""
    return web.query(BASE_PROJECTS_QUERY + """
        LEFT JOIN projects_points ON 
               (projects_points.location_id = locations.id AND projects_points.visible = 1)
        WHERE locations.visible = 1
            AND locations.type = 'point'
            AND projects_points.project_id = """ + str(int(project_id)) + """
        GROUP BY """ + LOCATIONS_GROUP_BY() + """, users.username
        ORDER BY last_comment DESC """ 
    + limit, vars=locals())
    
def points_count_by_project(project):
    project_id = project.id
    return web.query("""
        SELECT count(projects_points.project_id) as points_count
        FROM locations, projects_points
        WHERE locations.visible = 1
            AND locations.type = 'point'
            AND projects_points.location_id = locations.id
            AND projects_points.visible = 1
            AND projects_points.project_id = """ + str(int(project_id)) + """
        GROUP BY projects_points.project_id
    """, vars=locals())

def external_point_update(point, user):
    db_point = list(point_by_uuid(point.uuid) or [])
    if db_point:
        # !!! should we update lat, lon too?
        point.id = db_point[0].id
        web.query("""
            UPDATE locations
                SET title=$title
                WHERE id = $id
                ;
            """, vars=point.copy())
        # how to update tags???
        # tags_insert(point, user, point.tags, deny_namespaces=[])
        return "update"
    else:
        web.insert("locations", 
                    lat=point.lat, 
		    lon=point.lon, 
		    title=point.title,
                    uuid=point.uuid,
                    user_id=user.id, 
		    origin=point.origin,
                    added=point.added,  #!!!?
		    url=point.url)
        db_point = list(point_by_uuid(point.uuid))[0]
        tags_insert(db_point, user, point.tags, deny_namespaces=[])
        point.id = db_point.id
        return "insert"

def point_update(point, user):
    web.query("""
        UPDATE locations
            SET title=$title,
                uuid=$uuid
            WHERE id = $id
            ;
        """, vars=point.copy())

def point_full_update(point, user):
    web.query("""
        UPDATE locations
            SET title=$title,
                uuid=$uuid,
                lat=$lat,
                lon=$lon,
                visible=$visible,
                url=$url
            WHERE id = $id
            ;
        """, vars=point.copy())

def project_update(project, user):
    if "lat" not in project:
        web.query("""
        UPDATE locations
            SET title=$title,
                uuid=$uuid,
                origin=$origin,
                type='project'
            WHERE id = $id
            ;
        """, vars=project.copy())
    else:
        web.query("""
        UPDATE locations
            SET title=$title,
                uuid=$uuid,
                origin=$origin,
                lat=$lat,
                lon=$lon,
                type='project'
            WHERE id = $id
            ;
        """, vars=project.copy())

def triggers_by_id(id):
    return web.query("""
        SELECT DISTINCT *
        FROM triggers
        WHERE
            id = $id
    ;""", vars={'id': id})


def triggers_by_project_id(project_id):
    return web.query("""
        SELECT triggers.*
        FROM triggers
        WHERE
            triggers.project_id = $project_id
    ;""", vars={'project_id': project_id})

def triggers_by_project_id_with_condition(project_id, condition):
    return web.query("""
        SELECT triggers.*
        FROM triggers
        WHERE
            triggers.project_id = $project_id
            AND triggers.trigger_condition = $cond
    ;""", vars={'project_id': project_id, 'cond': condition})

def datasources_by_project_id(project_id):
    return web.query("""
        SELECT DISTINCT ds.*
        FROM datasources ds, locations_datasources lds
        WHERE
            lds.location_id = $project_id
            AND lds.datasource_id = ds.id
    ;""", vars={'project_id': project_id})

def datasources_by_id(id):
    return web.query("""
        SELECT DISTINCT *
        FROM datasources ds
        WHERE
            id = $id
    ;""", vars={'id': id})

def datasources_by_url_and_type(url, type_):
    return web.query("""
        SELECT DISTINCT *
        FROM datasources ds
        WHERE
            url = $url
            AND type = $type
    ;""", vars={'url': url, 'type': type_})

def datasource_insert(datasource, project, user):
    #!!! check for doubles
    ds_id = web.insert("datasources", 
        type=datasource.type,
        adapter=datasource.adapter,
        url=datasource.url,
        frequency=datasource.frequency,
        description=datasource.description)
    web.insert("locations_datasources", 
        datasource_id=ds_id,
        location_id=project.id,
        )
    return ds_id

def datasource_update(datasource, project, user):
    return web.update("datasources", where='id=$id',
        type=datasource.type,
        adapter=datasource.adapter,
        url=datasource.url,
        frequency=datasource.frequency,
        description=datasource.description,
        vars={'id': datasource.id},
    )

BASE_TAGS_QUERY = """
    SELECT tags.id as id,
           CONCAT(tags.tag_namespace, ':', tags.tag) as ns_tag,
           tags.tag as tag,
           tags.tag_namespace as tag_namespace,
           tag_namespaces.tag_system_id as tag_system_id,
           COUNT(DISTINCT locations_users_tags.location_id) as count_locations,
           COUNT(DISTINCT locations_users_tags.user_id) as count_users
    FROM tags
    LEFT JOIN tag_namespaces ON (tags.tag_namespace = tag_namespaces.id)
    LEFT JOIN locations_users_tags ON (locations_users_tags.tag_id = tags.id)
    """

def tags():
    return web.query(BASE_TAGS_QUERY + """
        LEFT JOIN locations ON (locations.visible = 1 AND locations.id = locations_users_tags.location_id)
        WHERE locations.type = 'point' OR locations.type = 'project'
        GROUP BY """ + TAGS_GROUP_BY + """
        ORDER BY tags.tag_namespace, tags.tag
    ;""", vars=locals())

def tags_of_points():
    return web.query(BASE_TAGS_QUERY + """
        LEFT JOIN locations ON (locations.visible = 1 AND locations.id = locations_users_tags.location_id)
        WHERE locations.type = 'point'
        GROUP BY """ + TAGS_GROUP_BY + """
        ORDER BY tags.tag_namespace, tags.tag
    ;""", vars=locals())


def tags_of_project_points(project):
    # !!! experimental
    project_id = project.id
    return web.query(BASE_TAGS_QUERY + """
        LEFT JOIN projects_points ON (projects_points.location_id = locations_users_tags.location_id AND projects_points.visible = 1)
        LEFT JOIN locations ON (locations.visible = 1 AND locations.id = locations_users_tags.location_id)
        WHERE locations.type = 'point'
            AND projects_points.project_id = $project_id
        GROUP BY """ + TAGS_GROUP_BY + """
        ORDER BY tags.tag_namespace, tags.tag
    ;""", vars=locals())


def tags_by_namespace(tag_namespace):
    return web.query(BASE_TAGS_QUERY + """
        LEFT JOIN locations ON (locations.visible = 1 AND locations.id = locations_users_tags.location_id)
        WHERE (locations.type = 'point' OR locations.type = 'project')
           AND tags.tag_namespace = $tag_namespace
        GROUP BY """ + TAGS_GROUP_BY + """
        ORDER BY tags.tag_namespace, tags.tag
    ;""", vars=locals())

def hide_point(point):
    web.query("""
        UPDATE locations
            SET visible = 0
            WHERE id = $id
            ;
    """, vars=point.copy())

    web.query("""
        UPDATE projects_points
            SET visible = 0
            WHERE location_id = $id
            ;
    """, vars=point.copy())

def hide_project(project):
    web.query("""
        UPDATE locations
            SET visible = 0
            WHERE id = $id
            ;
    """, vars=project.copy())

    # quick fix: otherwise count is broken!!!
    web.query("""
        DELETE FROM project_users
            WHERE project_id = $id
    """, vars=project.copy())

def hide_comment(comment):
    return web.query("""
        UPDATE notes
            SET visible = 0
            WHERE id = $id
            ;
    """, vars=comment.copy())

def delete_point(point):
    web.query("""
        DELETE FROM locations
            WHERE id = $id
            ;
    """, vars=point.copy())

    web.query("""
        DELETE FROM projects_points
            WHERE location_id = $id
            ;
    """, vars=point.copy())

    web.query("""
        DELETE FROM locations_users_tags
            WHERE location_id = $id
            ;
    """, vars=point.copy())

    web.query("""
        DELETE FROM notes
            WHERE location_id = $id
            ;
    """, vars=point.copy())


def delete_project(project):

    web.query("""
        DELETE FROM projects_points
            WHERE project_id = $id
    """, vars=project.copy())

    web.query("""
        DELETE FROM locations_datasources
            WHERE location_id = $id
    """, vars=project.copy())

    web.query("""
        DELETE FROM project_users
            WHERE project_id = $id
    """, vars=project.copy())

    web.query("""
        DELETE FROM locations_users_tags
            WHERE location_id = $id
            ;
    """, vars=project.copy())

    web.query("""
        DELETE FROM notes
            WHERE location_id = $id
            ;
    """, vars=project.copy())

    web.query("""
        DELETE FROM locations
            WHERE id = $id
    """, vars=project.copy())

    #triggers also!!!

def delete_comment(comment):
    web.query("""
        DELETE FROM notes 
            WHERE id = $id
    """, vars=comment.copy())

def delete_trigger(trigger):
    web.query("""
        DELETE FROM triggers 
            WHERE id = $id
    """, vars=trigger.copy())

def remove_point_from_project(point, project):
    web.query("""
        UPDATE projects_points
            SET visible = 0
            WHERE location_id = $point_id
                AND project_id = $project_id
            ;
    """, vars=dict(point_id=point.id, project_id=project.id))

def remove_datasource_from_project(ds, project):
    web.query("""
        DELETE FROM locations_datasources
            WHERE locations_datasources.location_id = $project_id
                AND locations_datasources.datasource_id = $ds_id
            ;
    """, vars=dict(ds_id=ds.id, project_id=project.id))


# !!! credentials is used in UM in two different meanings:
# just password, as in database 
# password, username in a {} fashion.
# !!! refactoring needed
def check_credentials(credentials):
    return web.query("""
        SELECT DISTINCT * FROM users
        WHERE
            credentials = $password
            AND upper(username) = upper($username)
    ;""", vars=credentials.copy())

def pwd_function(username):
    try:
        return list(web.query("""
        SELECT DISTINCT credentials FROM users
        WHERE upper(username) = upper($username)
    ;""", vars=vars()))[0].credentials
    except:
        raise ValueError, "Password not found"

def groups_by_user(user):
    return web.query("""
        SELECT groups.id as id, groupname 
        FROM group_users, groups 
        WHERE groups.id = group_users.group_id 
            AND user_id=$id;
    ;""", vars=user.copy())

def user_insert(user):
    return web.query("""
        INSERT INTO users (username, credentials, description) 
            VALUES ($username, $password, $description);
    """, vars=user.copy())

def user_update(user):
    web.update("users", where='id=$id',
                credentials=user.password,
                vars=user.copy(),
    )

def profile_update(user, profile):
    for k, v in profile.items():
        web.query("""
            DELETE FROM user_profiles
                WHERE user_id = $user_id 
                AND prop_key=$prop_key;
        """, vars=dict(user_id=user.id, prop_key=k,))
        web.query("""
            INSERT INTO user_profiles (user_id, prop_key, prop_value) 
                VALUES ($user_id, $prop_key, $prop_value);
        """, vars=dict(user_id=user.id, 
                       prop_key=k, 
                       prop_value=v))

def search_profile_email(email):
    return web.query("""
        SELECT user_id FROM user_profiles
            WHERE prop_key = $prop_key
                AND LOWER(prop_value) = LOWER($prop_value);
    """, vars=dict(prop_key="email", prop_value=email))

def user_profile(user):
    return dict([(p.prop_key, p.prop_value) for p in web.query("""
            SELECT * FROM user_profiles
                WHERE user_id = $user_id;
        """, vars=dict(user_id=user.id,))])


def object_profile(object):
    return dict([(p.prop_key, p.prop_value) for p in web.query("""
            SELECT * FROM location_profiles
                WHERE location_id = $location_id;
        """, vars=dict(location_id=object.id,))])

def object_profile_update(object, profile):
    for k, v in profile.items():
        web.query("""
            DELETE FROM location_profiles
                WHERE location_id = $location_id 
                AND prop_key=$prop_key;
        """, vars=dict(location_id=object.id, prop_key=k,))
        if v is not None:
            web.query("""
                INSERT INTO location_profiles (location_id, prop_key, prop_value) 
                    VALUES ($location_id, $prop_key, $prop_value);
            """, vars=dict(location_id=object.id, 
                           prop_key=k, 
                           prop_value=v))

def search_object_profiles(key, value):
    # not tested!!! not used!!!
    return web.query("""
        SELECT location_id FROM location_profiles
            WHERE prop_key = $prop_key
                AND LOWER(prop_value) = LOWER($prop_value);
    """, vars=dict(prop_key=key, prop_value=value))


def note_profile(object):
    return dict([(p.prop_key, p.prop_value) for p in web.query("""
            SELECT * FROM note_profiles
                WHERE note_id = $note_id;
        """, vars=dict(note_id=object.id,))])

def note_profile_update(object, profile):
    for k, v in profile.items():
        web.query("""
            DELETE FROM note_profiles
                WHERE note_id = $location_id 
                AND prop_key=$prop_key;
        """, vars=dict(note_id=object.id, prop_key=k,))
        if v is not None:
            web.query("""
                INSERT INTO note_profiles (note_id, prop_key, prop_value) 
                    VALUES ($note_id, $prop_key, $prop_value);
            """, vars=dict(note_id=object.id, 
                           prop_key=k, 
                           prop_value=v))

def search_note_profiles(key, value):
    # not tested!!! not used!!!
    return web.query("""
        SELECT note_id FROM note_profiles
            WHERE prop_key = $prop_key
                AND LOWER(prop_value) = LOWER($prop_value);
    """, vars=dict(prop_key=key, prop_value=value))


def group_update(user, group):
    #!!! delete?
    web.query("""
        DELETE FROM group_users
            WHERE user_id = $user_id 
            AND group_id = $group_id;
    """, vars=dict(user_id=user.id, group_id=group.id))
    return web.query("""
        INSERT INTO group_users (user_id, group_id) 
            VALUES ($user_id, $group_id);
    """, vars=dict(user_id=user.id, group_id=group.id))

def groups():
    return web.query("""SELECT * from groups;""")

def group_by_id(id):
    return web.query("""SELECT *
            FROM groups WHERE id=$id;""", vars=dict(id=id))

def group_by_name(groupname):
    return web.query("""SELECT *
            FROM groups WHERE groupname=$groupname;""", vars=dict(groupname=groupname))

def delete_user_by_description(description):
    """ Description is used to temporary store some info"""
    web.query("""
        DELETE FROM users 
            WHERE description = $description
    """, vars=dict(description=description))

def user_by_description(description):
    return web.select("users", where="description=$description", 
                      vars=dict(description=description))

def user_by_location_role(location):
    return web.query("""SELECT """ + USERS_GROUP_BY + """
            FROM users, locations_policy_table
            WHERE locations_policy_table.user_id = users.id
              AND locations_policy_table.location_id=$location_id
            GROUP BY """ + USERS_GROUP_BY + """;""", 
            vars=dict(location_id=location.id))
    


def update_user_description(user, description):
    return web.query("""
        UPDATE users
            SET description = $description
            WHERE id = $id
            ;
    """, vars=dict(id=user.id, description=description))


def version():
    return web.query("""
        SELECT version as "Latest patch:", added as "Applied at:" 
            FROM version ORDER BY added DESC
    """)

def db_version():
    return web.query("""
        SELECT version();
    """)

def num_of_records(table):
    return web.query("""
        SELECT count(*) as "count" FROM %s;
    """ % table)

def locations_stats():
    return web.query("""
        select count(*) as "count", type, origin, visible
        from locations 
        group by type, origin, visible;""")

def check_connection():
    return web.query("""SELECT 2 + 2;""")

def get_policies(object, user):
    return web.query("""
        SELECT role 
        FROM locations_policy_table
        WHERE user_id = $user_id 
            AND location_id=$location_id;
    ;""", vars={'user_id': user.id, 'location_id': object.id})

def set_policies(object, user, roles, adder_user):
    for role in roles:
        web.insert("locations_policy_table", 
            user_id=user.id,
            location_id=object.id,
            adder_user_id=adder_user.id,
            role=role
        )

def unset_policies(object, user, roles, adder_user):
    for role in roles:
        web.query("""
        DELETE FROM locations_policy_table
            WHERE user_id = $user_id 
            AND location_id=$location_id
            AND role=$role
        ;""", vars={'user_id': user.id, 'location_id': object.id,
            'role': role})

def enable_point_by_id(point_id, user):
    web.query("""
        UPDATE locations
            SET visible=1,
                user_id=$user_id
            WHERE id = $id
            ;
        """, vars={'id': point_id, 'user_id': user.id})

    web.query("""
        UPDATE projects_points
            SET visible=1
            WHERE location_id = $id
            ;
        """, vars={'id': point_id})

def replace_and_delete_user(old_user_id, user_id):
    web.query("""
        UPDATE locations_users_tags
            SET   user_id=$user_id
            WHERE user_id = $old_user_id
            ;
        """, vars={'user_id': user_id, 'old_user_id': old_user_id})

    web.query("""
        UPDATE notes
            SET   user_id=$user_id
            WHERE user_id = $old_user_id
            ;
        """, vars={'user_id': user_id, 'old_user_id': old_user_id})

    web.query("""
        DELETE FROM users
            WHERE id = $old_user_id
            ;
        """, vars={'old_user_id': old_user_id})

