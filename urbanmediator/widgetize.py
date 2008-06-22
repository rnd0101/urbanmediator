# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Widgetizers (widget factories). 
"""
import web
from web.utils import Storage

import model
import i18n
import config
import util
import webutil
import webform as form
from links import widget_links, pc_links
from view import pc_macro as macros, pc_render as render, \
                pc_get_page as get_page
import widget

_ = i18n._


def common_widget_form(**args):
    return [
    form.Fieldset('fieldset', description=_("Widget appearance")),
    form.Hidden('from_widget', description='', value="1", style="display:none;"),
    form.Hidden('id', description='', value="", style="display:none;"),
    form.Checkbox("showhome",
        description=_("Show header?"),
    ), 
    form.Checkbox("showlogo",
        description=_("Show logo?"),
    ), 
    form.Textbox("widget_context_title",
        description=_("Title"),
    ),
    form.Textbox("widget_context_url", 
        description=_("Link for title (URL)"),
    ),
    form.Textbox("widget_title", 
        description=_("Subtitle"),
    ),

    form.Textbox("height", 
        form.regexp('[0-9.]+', _('Must be a number')),
        description=_("Height (pixels)"),
        value=str(args["height"]),
    ),
    form.Textbox("width", 
        form.regexp('[0-9.-]+', _('Must be a number')),
        description=_("Width (pixels)"),
        value=str(args["width"]),
    ),
    form.Fieldset('end_of_fieldset'),
    ]

class Widgetize:
    """Abstract widgetizer
    Subclasses should provide: title, widget_link, widgetizer_link,
    .get_form()
    """
    title = ""
    widget_link = ""
    widgetizer_link = ""

    def get_form(self, **kwargs):
        pass

    def GET(self, topic_id): 
        topics, topic = model.t_helper(topic_id)

        webinput = web.input()

        context = Storage(title=_(self.title),
                          widgetizer_link=pc_links(self.widgetizer_link, topic_id),
                          help_link=pc_links('guide', 'help_' + self.widget_link),
                        )
        form = self.get_form(topic=topic)

        if not webinput.has_key("from_widget") or not form.validates():
            get_page("widgetize", context, topic, form)
        else:
            #d = Storage()
            #for k in form.d:
            #    if form.d[k]:
            #        d[k] = form.d[k]
            widget_link = widget_links(self.widget_link, topic.id, **form.d)
            result = Storage(
                link=widget_link,
                link_len=len(widget_link),
                height=form.d.height,
                width=form.d.width,
            )
            result.id = form.d.get("id", "")
            get_page("widgetize", context, topic, form, result=result)

    POST = GET


############# Submit button widget ###############################

class SubmitWidgetize(Widgetize):

    title = "Add Point Button Widget Factory"
    widget_link = "submit"
    widgetizer_link = "tools_submit_widgetize"

    def get_form(self, **kwargs):
        topic = kwargs.get("topic", None)
        if "zoom" in topic.profile:
            zoom = topic.profile.zoom
        else:
            zoom = config.topic_zoom
        return form.Form(*[
    form.Fieldset('fieldset', description=_("Widget Basic Settings")),
    form.Textbox("title",
        form.required,
        form.Validator(_('Must be filled'), lambda x:x.strip()),
        description=_("Text that will show on button"),
    ), 
    form.Textbox("disabled_text",
        description=_("Text to show when point creation is disabled"),
        value=_("Adding point disabled")
    ), 
    form.Fieldset('end_of_fieldset'), 
    form.Fieldset('fieldset', description=_("Add Point page Basic Settings")),
    form.Textbox("title_example",
        description=_("Point title example"),
    ), 
    form.Textbox("fixed_tags",
        description=_("List of fixed hidden tags"),
    ), 
    form.Textbox("tags_for_menu",
        description=_("List of predefined tags (leave empty for none)"),
    ), 
    form.Dropdown("free_tags",
        [("allow", _("Allow")), ("disallow", _("Disallow"))],
        description=_("Free tags (user's own)"),
        size=1,
#<small>$_("Empty for most cases. May be: official")</small>
    ),

    form.Textbox("tags_example",
        description=_("Point Tags example (for free tags)"),
    ), 
    form.Fieldset('end_of_fieldset'), 
    form.Fieldset('fieldset', description=_("Add Point page Advanced Settings (optional)")),
    #form.Textbox("form_title",
    #    description=_("Form title"),
    #), 
    form.Textbox("c_lat", 
        form.regexp('[0-9.-]+|', _('Must be a number')),
        description=_("Latitude"),
    ),
    form.Textbox("c_lon", 
        form.regexp('[0-9.-]+|', _('Must be a number')),
        description=_("Longitude"),
    ),
    form.Textbox("zoom", 
        form.regexp('[12]?[0-9]|auto|', _('Must be a number 1-20 or auto')),
        form.Validator(_('Must be 1-20'), lambda x:x.lower() == "auto" or 1 < int(x) < 20),
        description=_("Zoom level"),
        value=zoom,
    ),
    form.Textbox("template",
        form.regexp('[0-9]+|', _('Must be a number or empty')),
        description=_("Template point ID"),
    ), 
    form.Fieldset('end_of_fieldset'), 
    ] + common_widget_form(height=36, width=200)
    )()


############# Note widget ###############################

class NoteWidgetize(Widgetize):

    title = "Note Widget Factory"
    widget_link = "note"
    widgetizer_link = "tools_note_widgetize"

    def get_form(self, **kwargs):
        return form.Form(*[
    form.Fieldset('fieldset', description=_("Note widget information")),
    form.Textbox("title",
        form.required,
        form.Validator(_('Must be filled'), lambda x:x.strip()),
        description=_("Note title (not shown)"),
    ), 
    form.Editor("text",
        description=_("Note text"),
    ), 
    form.Fieldset('end_of_fieldset'), 
    ] + common_widget_form(height=36, width=200)
    )()


############# Container widget ###############################

class ContainerWidgetize(Widgetize):

    title = "Container widget"
    widget_link = "container"
    widgetizer_link = "tools_container_widgetize"

    def get_form(self, **kwargs):
        return form.Form(*[
    form.Fieldset('fieldset', description=_("Container widget information")),
    form.Textbox("title",
        form.required,
        form.Validator(_('Must be filled'), lambda x:x.strip()),
        description=_("Title"),
    ), 

    form.Textbox("u0", 
        description=_("URL1"),
    ),
    form.Textbox("u1", 
        description=_("URL2"),
    ),
    form.Textbox("u2", 
        description=_("URL3"),
    ),
    form.Textbox("u3", 
        description=_("URL4"),
    ),
    form.Textbox("u4", 
        description=_("URL5"),
    ),
    form.Textbox("u5", 
        description=_("URL6"),
    ),
    form.Textbox("u6", 
        description=_("URL7"),
    ),
    form.Textbox("u7", 
        description=_("URL8"),
    ),
    form.Fieldset('end_of_fieldset'),
    ] + common_widget_form(height=36, width=200)
    )()


############# Topic points widget ###############################

class TopicPointsWidgetize(Widgetize):

    title = "Topic Points Widget Factory"
    widget_link = "topic_points"
    widgetizer_link = "tools_topic_points_widgetize"

    def get_form(self, **kwargs):
        topic = kwargs.get("topic", None)
        return form.Form(*[
    form.Fieldset('fieldset', description=_("Topic Points widget information")),
    form.Hidden('from_widget', description='', value="1", style="display:none;"),
    form.Textbox("title",
        form.required,
        form.Validator(_('Must be filled'), lambda x:x.strip()),
        description=_("Title"),
    ), 
    form.Textbox("number_of_points", 
        form.regexp('[12]?[0-9]|', _('Must be a number 1-20')),
        form.Validator(_('Must be 1-20'), lambda x:1 < int(x) < 20),
        description=_("Number of points to show"),
        value="5",
    ),
    form.Textbox("point_list_show",
        description=_("Point information display in point list"),
        value=topic.profile.point_list_show,
    ), 
    form.Dropdown("order",
        [(o, _(o))
            for o in config.main_page_point_orders],
        description=_("Point order"),
        size=1,
    ),
    form.Fieldset('end_of_fieldset'), 
    ] + common_widget_form(height=100, width=200)
    )()

############# Map widget ###############################

class MapWidgetize(Widgetize):

    title = "Map Widget Factory"
    widget_link = "map"
    widgetizer_link = "tools_map_widgetize"

    def get_form(self, **kwargs):
        return form.Form(*[
    form.Fieldset('fieldset', description=_("Map widget information")),
    form.Hidden('from_widget', description='', value="1", style="display:none;"),
    form.Textbox("title",
        form.required,
        form.Validator(_('Must be filled'), lambda x:x.strip()),
        description=_("Title"),
    ), 
    form.Textbox("mapwidth", 
        description=_("Width of the map"),
        value="200",
    ),
    form.Textbox("mapheight", 
        description=_("Height of the map"),
        value="200",
    ),
    form.Fieldset('end_of_fieldset'), 
    ] + common_widget_form(height=200, width=200)
    )()

############# Topic points widget ###############################

class TopicLinksWidgetize(Widgetize):

    title = "Topic Links Widget Factory"
    widget_link = "topic_links"
    widgetizer_link = "tools_topic_links_widgetize"

    def get_form(self, **kwargs):
        return form.Form(*[
    form.Fieldset('fieldset', description=_("Topic Links widget information")),
    form.Hidden('from_widget', description='', value="1", style="display:none;"),
    form.Textbox("title",
        form.required,
        form.Validator(_('Must be filled'), lambda x:x.strip()),
        description=_("Title"),
    ), 
    form.Textbox("number_of_links", 
        form.regexp('[12]?[0-9]|', _('Must be a number 1-20')),
        form.Validator(_('Must be 1-20'), lambda x:1 < int(x) < 20),
        description=_("Number of links to show"),
        value="5",
    ),
    form.Fieldset('end_of_fieldset'), 
    ] + common_widget_form(height=100, width=200)
    )()

############# Widget Editor ###############################

class WidgetEditor:

    def GET(self, topic_id): 
        topics, topic = model.t_helper(topic_id)

        webinput = web.input()

        context = Storage(title=_("Widget Editor"))

        q = webutil.get_query(webinput.url)
        q.id = webinput.id  # comment id

        # !!! ugly! make better
        if "/submit" in webinput.url:
            web.seeother(pc_links("tools_submit_widgetize", topic.id, q))
        elif "/note" in webinput.url:
            web.seeother(pc_links("tools_note_widgetize", topic.id, q))
        elif "/container" in webinput.url:
            web.seeother(pc_links("tools_container_widgetize", topic.id, q))
        elif "/topic_points" in webinput.url:
            web.seeother(pc_links("tools_topic_points_widgetize", topic.id, q))
        elif "/topic_links" in webinput.url:
            web.seeother(pc_links("tools_topic_links_widgetize", topic.id, q))
        elif "/map" in webinput.url:
            web.seeother(pc_links("tools_map_widgetize", topic.id, q))

############# Widget Mover ###############################

class WidgetMove:

    def GET(self, topic_id):
        i = web.input()
        topics, topic, comments, comment = model.t_c_helper(topic_id, i.id)

        context = Storage(title=_("Widget Editor"))

        topic.comments.filter_by_type(comment_type="widget")
        topic.comments.sort_by_order()

        # Making new order
        cnt = 0
        for c in topic.comments:
            cnt += 1
            c.ord = cnt * 2 + 2
            if int(c.id) == comment.id:
                if i.dir == 'up':
                    c.ord -= 3
                else:
                    c.ord += 3

        # Saving order
        topic.comments.store_order()

        web.seeother(pc_links("topic_widgets", topic.id))
