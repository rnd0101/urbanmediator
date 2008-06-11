# -*- coding: utf-8 -*-

import web

import re, urllib, datetime

import config, i18n
import feed_data
from web.utils import Storage
from webutil import request_uri
from session_user import *
import session
import links
import util

URL_RE = re.compile("((?:feed:|source:)?(?:(?:http|ftp|https|query)://|/media)\S*)")

try:
    local_doc_render = web.template.render(config.local_docs_dir, cache=config.cache)
except:
    local_doc_render = None

doc_render = web.template.render('docs/', cache=config.cache)
pc_render = web.template.render('templates/pc/', cache=config.cache)
mobile_render = web.template.render('templates/mobile/', cache=config.cache)

pc_macro = mobile_macro = web.template.render('templates/macros/', cache=config.cache)

feed_render = web.template.render('templates/feed/', cache=config.cache)

widget_render = web.template.render('templates/widget/', cache=config.cache)

def _doc_render(template_name):

    lang_specific_template = template_name +"_%s" % i18n.getLanguage()
    default_lang_template = template_name +"_en"
    
    render = None

    # 1. local doc render with specific language
    if local_doc_render:
        render = getattr(local_doc_render, lang_specific_template, None)
    if render is not None:
        return render

    # 2. doc render with specific language
    render = getattr(doc_render, lang_specific_template, None)
    if render is not None:
        return render

    # 3. local doc english
    if local_doc_render:
        render = getattr(local_doc_render, default_lang_template, None)
    if render is not None:
        return render

    # 4. doc english
    render = getattr(doc_render, default_lang_template, None)
    if render is not None:
        return render

    return None

    # 5. local doc no language
    if local_doc_render:
        render = getattr(local_doc_render, template_name, None)
    if render is not None:
        return render

    # 6. doc no language
    render = getattr(pc_render, template_name, None)
    if render is not None:
        return render

class DocRender:
    """ Syntactic support for doc_render.attr style of access
    """
    def __getattr__(self, template_name):
        return _doc_render(template_name)()

docs = DocRender()

styles = util.Links({
})


def pc_page_context(context=None):
    context = context or Storage()
    if not context.has_key("user"):
        context.user =  get_user()
    if not context.has_key("user_location"):
        context.user_location = session.get_user_location()

    context.setdefault("disallow_robots", config.disallow_robots)

    context.setdefault("title", '')
    context.setdefault("message", web.input().get('message', ''))
    return context


def pc_get_page(template_name, context, *args, **kwargs):
    context = pc_page_context(context)
    context.setdefault("page_specific_styles", styles.get(template_name, []))
    context.setdefault("page_specific_js", )
    context.setdefault("linktarget", '')
    context.setdefault("lnktgt", '')  # all links have this

    if not context.has_key("feeds"):
        context.setdefault("feeds", [])

    try:
        page = getattr(pc_render, template_name)
    except:
        raise  #!!!
        page = getattr(pc_render, "old_" + template_name)
    print pc_render.base( page(context, cache=config.cache, *args, **kwargs), context, cache=config.cache )


def get_widget(template_name, context, *args, **kwargs):
    context = context or Storage()
#    if not context.has_key("user"):
#        context.setdefault("user", get_user())
    if not context.has_key("feeds"):
        context.setdefault("feeds", [
                ])
    context.setdefault("widget", True)
    context.setdefault("linktarget", ' target="_top" ')  # optional link targets
    context.setdefault("lnktgt", ' target="_top" ')  # all links have this

    context.setdefault("onlycode", False)
    context.setdefault("title", '')
    context.setdefault("page_specific_js", '')
    context.setdefault("page_specific_styles", styles.get(template_name, []))
    context.setdefault("nocache", True)
    context.setdefault("debug", config.debug_mode)
    context.setdefault("message", web.input().get('message', ''))
    try:
        page = getattr(widget_render, template_name)
    except:
        page = getattr(widget_render, "old_" + template_name)

    if context.onlycode:  # for internal inline HTML widget no base needed
        return page(context, cache=config.cache, *args, **kwargs)

    print widget_render.base( page(context, cache=config.cache, *args, **kwargs), context, cache=config.cache )


def get_feed(context, template_name="feed", *args, **kwargs):
    context = context or Storage()
    context.setdefault("self_url", request_uri())
    if not context.has_key("user"):
        context.setdefault("user", get_user())
    context.setdefault("title", "no title")
    context.setdefault("subtitle", "no subtitle")
    context.setdefault("debug", False)
    page = getattr(feed_render, template_name)
    print page(context, *args, **kwargs)


def mobile_get_page(template_name, context, *args, **kwargs):
    context = context or Storage()
    if not context.has_key("user"):
        context.setdefault("user", get_user())

    context.setdefault("widget", False)
    context.setdefault("linktarget", '')
    context.setdefault("lnktgt", '')  # all links have this

    context.setdefault("disallow_robots", config.disallow_robots)

    context.setdefault("title", '')
    context.setdefault("page_specific_js", '')
    context.setdefault("page_specific_styles", styles.get(template_name, []))
    context.setdefault("nocache", True)
    context.setdefault("debug", config.debug_mode)
    context.setdefault("message", web.input().get('message', ''))
    try:
        page = getattr(mobile_render, template_name)
    except:
        raise
        page = getattr(mobile_render, "old_" + template_name)
    print mobile_render.base(
        page(context, cache=config.cache, *args, **kwargs), 
            context, cache=config.cache )



def dist_meters(coord_distance):
    if int(coord_distance) < 2000:
        return str(int(coord_distance)) + " " + i18n._("m")
    else:
        return ("%3.1f" % (int(coord_distance) / 1000.) + " " + i18n._("km")).replace(".0", "")

def shorten_url(url, max_length=46):
    if len(url) <= max_length:
        return url
    urlrepr = urllib.unquote(url)
    if len(urlrepr) > max_length:
        urlrepr = urlrepr[:max_length//2] + "…" + urlrepr[-(max_length//2-1):]
    return urlrepr

def mark_urls(m):
    url = m.groups()[0]
    file_label = i18n._("File")

    if url.startswith("query:"):
        return "" # no queries supported

        # the following code may be revived in the future
        try:
            parts = url.split("/", 3)[2:4]
            to_ret = ""
            for l, rs, r, t in feed_data.get_query_results(query=parts[1], url=parts[0]):
                to_ret += '<br><a href="%s">%s</a> %s<br>Tags: ' % (l.encode("utf-8"), rs.encode("utf-8"), r.encode("utf-8"))
                for tt in t:
                    to_ret += '[' + tt + '] '
                to_ret += ''
            return to_ret
        except:
            return "ERROR: " + url
       
    if url.startswith("source:"):
        return i18n._("This information is stored at:")
        return """<a href="%s">%s</a>""" % (url[7:], i18n._("Also stored at"))

    if url.startswith("feed:"):
        flocs = feed_data.fetch_feed([url[5:]])
         
        fp = """<ul class="feedlist">"""
        fmt = """<li><a href="%(url)s">%(title)s</a> %(text)s</li>"""

        entry_l = []
        for fl in flocs:
            etxt = fl["text"]
            if "<" not in etxt and ">" not in etxt:    #!!! always true?
                fl["text"] = URL_RE.sub(mark_urls, etxt)
            entry_l.append(fmt % fl)

        txt = """<ul class="feedlist">""" + "\n".join(entry_l) + "</ul>"
        s_url = shorten_url(url[5:])
        txt = """<a href="%(url)s">%(s_url)s</a>\n<br>""" % vars() + txt
        return txt
    if url.startswith("/media"):
        url = config.base_url + url
        return """<a href="%(url)s"><img src="%(url)s&amp;preview=1" alt="[%(file_label)s]" /></a>""" % vars()
        # or if PIL not available:
        return """<a href="%(url)s">[%(file_label)s]</a>""" % vars()
    if url.startswith("/"):  # not /media
        return url
    s_url = shorten_url(url)
    return """<a href="%(url)s">%(s_url)s</a>""" % vars()

def render_text(text):
    if "<" in text or ">" in text:
        return text
    return URL_RE.sub(mark_urls, text)


ICONS = {
    'official': 'blue',
    'external': 'green',
    'go': 'arrow',
    'hi': 'highlighted',
    'DEFAULT_COLOR': 'red',
    'DEFAULT_MOD': '',
}

def render_point_class(loc, hi):
    if hi:
        return "point_hi_" + loc.origin
    else:
        return "point_" + loc.origin

def render_point_icon_url(loc, hi):
    hi = hi or ''
    if hi == True:
        hi = 'hi'
    modifier = ICONS.get(hi, ICONS["DEFAULT_MOD"])
    color = ICONS.get(loc.origin, ICONS["DEFAULT_COLOR"])
    name = "_".join(filter(None, (color, modifier)))
    return config.schema_base_url + "/point/" + name + ".png"

def i18n_datestr(then, now=None):
    """
    Converts a datetime object to a nice string representation.
    """
    def agohence(n, what, divisor=None):
        if divisor:
            n = n // divisor

        wwhat = "%%s %s" %  what
        n_what = i18n.n_(wwhat, wwhat + "s", abs(n)) % abs(n)
        if n < 0:
            return i18n._("%s from now") % n_what
        else:
            return i18n._("%s ago") % n_what

    oneday = 86400   # == 24 * 60 * 60
    onehour = 3600   # == 60 * 60

    if not now:
        now = util.now()
    delta = now - then
    deltaseconds = int(delta.days * oneday + delta.seconds + delta.microseconds * 1e-06)
    deltadays = abs(deltaseconds) // oneday
    if deltaseconds < 0: 
        deltadays *= -1 # fix for oddity of floor

    if deltadays:
        if abs(deltadays) < 4:
            return agohence(deltadays, 'day')

        datedict = dict(
            day = then.day,
            monthname = i18n._("%s_month" % then.month),
            month = then.month,
            year = then.year,
        )
        if then.year != now.year or deltadays < 0:
            return i18n._("%(day)s.%(month)s.%(year)s") % datedict
        return i18n._("%(day)s.%(month)s") % datedict

    if int(deltaseconds):
        if abs(deltaseconds) > onehour:
            return agohence(deltaseconds, 'hour', onehour)
        elif abs(deltaseconds) > 60:
            return agohence(deltaseconds, 'minute', 60)
        else:
            return agohence(deltaseconds, 'second')

    return agohence(1, 'second')  #!!! no milli/micro


    deltamicroseconds = delta.microseconds
    if delta.days:
        deltamicroseconds = int(delta.microseconds - 1e6) # datetime oddity
    if abs(deltamicroseconds) > 1000:
        return agohence(deltamicroseconds, 'millisecond', 1000)

    return agohence(deltamicroseconds, 'microsecond')


def render_date(date, label="datetime_format", none_repr=""):
    if not hasattr(date, "strftime"):
        return none_repr
    if label == "rfc3339":
        fmt = '%Y-%m-%dT%H:%M:%SZ'
    elif hasattr(config, "datetime_format_local"):
        fmt = config.datetime_format_local
    else:
        fmt = str(i18n._(label))
        if fmt == label:
            fmt = config.datetime_format
    return date.strftime(fmt)

def rel_date(date):
    return i18n_datestr(date)

def long_lang_name(lang):
    import languages
    return languages.languages.get(lang, lang)



def render_editor(name, value):
    import fckeditor, i18n
    sBasePath = links.pc_links.fckeditor_base

    oFCKeditor = fckeditor.FCKeditor(name)
    oFCKeditor.BasePath = sBasePath
    oFCKeditor.Value = render_text(value or "")
    oFCKeditor.Config = {"CustomConfigurationsPath": 
        links.pc_links("editor_base_url", 
            AutoDetectLanguage="false",
            DefaultLanguage=i18n.getLanguage())
    }
    return oFCKeditor.Create()

def render_url(s):
    """Minimally guard URL """
    return s.replace("&", "&amp;")

def official_icon():
    if "http://" in config.official_icon:
        return config.official_icon
    else:
        return links.pc_links.static + config.official_icon

web.template.Template.globals.update(dict(
  doc=docs,
  long_lang_name=long_lang_name,
  mobile_macro=mobile_macro,
  macro=pc_macro,
  datestr=web.datestr,
  dist_meters=dist_meters,
  config=config,
  ctx=web.ctx,
  int=int,
  render_text=render_text,
  render_date=render_date,
  render_editor=render_editor,
  render_url=render_url,
  rel_date=rel_date,
  render_point_class=render_point_class,
  render_point_icon_url=render_point_icon_url,
  base_url=config.base_url,
  schema_base_url=config.schema_base_url,
  debug_mode=config.debug_mode,
  _=i18n._,
  n_=i18n.n_,
  LANG=i18n.getLanguage,
  loc_digest=util.loc_digest,
  dictmerge=util.dictmerge,
  enumerate=enumerate,
  first_line=util.first_line,
  official_icon=official_icon,
))
