# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

     Urban Mediator -- Access Control List

    Defines and maintains data structures for access control to 
    UM objects and actions. Helps authorize certain actions
    and make check in the templates.
"""

import model
import session_user

class PolicyTable:
    """
    The main dispatcher for the authorization
    """

    def __init__(self, policies=None, for_whom=None):
        """
        policies -- list of policy table to abide
        for_whom -- set user. Otherwise get_user() is used
        """
        self._for_whom = for_whom
        self._policies = policies

    def _user(self):
        """
        Gets the user for whom to authorize
        """
        
        if self._for_whom is None:
            u = session_user.get_user()
        else:
            u = self._for_whom
        return u

    def show_login(self):
        u = self._user()
        if u is None: return True
        return False

    def is_current_user(self, user):
        u = self._user()
        if u is None or user is None: return False
        try:
            return int(u.id) == int(user.id)
        except:
            pass
        return False

    def manage_topic(self, topic):
        """
        Checks if the user is authorized to delete the topic
        """
        u = self._user()

        if u is None: return False
        if "administrators" in u.groupnames: return True
        if topic.author == u.username: return True  #redundant?
        if model.Projects.allows(topic, u, "manage_project"):
            return True
        return False

    def delete_topic(self, topic):
        return self.manage_topic(topic)

    def view_user_settings(self, user):
        if "guests" in user.groupnames: return False
        u = self._user()
        if u is None: return False
        if "administrators" in u.groupnames: return True
        if user.id == u.id: return True
        return False

    def show_topic_tools(self, topic):
        u = self._user()
        if u is None: return False
        return True

    def change_user_settings(self, user):
        if "guests" in user.groupnames: return False
        u = self._user()
        if u is None: return False
        if "administrators" in u.groupnames: return True
        if user.id == u.id: return True
        return False

    def manage_topic_admins(self, topic):
        u = self._user()

        if u is None: return False
        if "administrators" in u.groupnames: return True
        if model.Projects.allows(topic, u, "manage_users"):
            return True
        return False

    def delete_topic(self, topic):
        # what if we have/do not have points?!!!
        # should we have flexible delete (e.g. 
        # delete outright if empty?)
        return self.manage_topic(topic)

    def change_topic_settings(self, topic):
        return self.manage_topic(topic)

    def manage_point(self, topic, point):
        """
        Checks if the user is authorized to delete the point
        """
        u = self._user()

        if u is None: return False
        if "administrators" in u.groupnames: return True
        # if topic is not active: return False
        if point.author == u.username: return True
        return False

    def delete_point(self, topic, point):
        u = self._user()
        if u is None: return False
        # topic owner has right to manage the point
        try:
            topic_owner_rights = topic.profile.get("topic_owner_rights", "topic_only")
        except:
            return self.manage_point(topic, point)
        if topic_owner_rights == "topic_and_points" \
            and self.manage_topic(topic):
            return True
        return self.manage_point(topic, point)

    def edit_point(self, topic, point):
        return self.manage_point(topic, point)

    def add_point(self, topic):
        """Is it ok to actually add a point"""
        try:
            allowed = topic.profile.point_contributors
        except:
            allowed = "visitors"
        if allowed == "nobody": return False
        u = self._user()
        if allowed == "anyone": return True  # careful!
        if u is None: return False
        # !!!this is not yet fully specified!
        if "guests" in u.groupnames and allowed == "registered": 
            return False
        if allowed == "topic administrators":
            return self.manage_topic(topic)
        return True

    def add_point_by_user(self, topic, user):
        """Is it ok to actually add a point"""
        try:
            allowed = topic.profile.point_contributors
        except:
            allowed = "visitors"
        if allowed == "nobody": return False
        u = user
        if allowed == "anyone": return True  # careful!
        if u is None: return False
        # !!!this is not yet fully specified!
        if "guests" in u.groupnames and allowed == "registered": 
            return False
        if allowed == "topic administrators":
            return self.manage_topic(topic)
        return True

    def show_add_point(self, topic):
        """Is it ok to show Add point button to the user? """
        try:
            allowed = topic.profile.get("point_contributors", "guests")
        except:
            return True   #!!! need better defaults?
        if allowed == "nobody": return False
        return True

    def mark_inappropriate_point(self, topic, point):
        """Who can mark point as an inappropriate?"""
        u = self._user()
        if u is None: return False
        if "guests" in u.groupnames: return False
        return True

    def manage_special_tags(self):
        """Who can remove special: tags"""
        u = self._user()
        if u is None: return False
        if "administrators" in u.groupnames: return True
        return False

    def add_topic(self):
        u = self._user()

        if u is None: return False
        if "guests" in u.groupnames: return False
        # ??? what if topic is readonly?
        return True

    def subscribe_topic(self, topic):
        u = self._user()

        if u is None: return False
        if "guests" in u.groupnames: return False
        return True

    def add_comment(self, topic, point):
        u = self._user()

        if u is None: return False
        # ???
        return True

    def tag_point(self, topic, point):
        u = self._user()

        if u is None: return False
        # ???
        return True


    def manage_comment(self, topic, point, comment):
        u = self._user()

        if u is None: return False
        if "administrators" in u.groupnames: return True
        # point author can delete comment (?)
        if point.author == u.username: return True
        if comment.author == u.username: return True
        # ???
        return False
        
    def edit_comment(self, topic, point, comment):
        return self.manage_comment(topic, point, comment)

    def delete_comment(self, topic, point, comment):
        return self.manage_comment(topic, point, comment)

    def manage_um(self):
        u = self._user()

        if u is None: return False
        if "administrators" in u.groupnames: return True
        return False

    def manage_users(self):
        return self.manage_um()

    def change_um_settings(self):
        return self.manage_um()


#: list of rules to authorize actions
AUTHORIZATION_POLICY = []
#: list of rules to recommend actions
RECOMMENDATION_POLICY = []

authorize = PolicyTable(policies=[AUTHORIZATION_POLICY])
recommend = PolicyTable(policies=[RECOMMENDATION_POLICY])
