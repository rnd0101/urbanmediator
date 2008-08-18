# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    I18n helper functions. Note dependency on web.py.

"""

import config
import web
import gettext

LOCALES_DIR = config.LOCALES_DIR
LANGUAGES = config.LANGUAGES

# From zope/publisher/browser.py

def normalize_lang(lang):
    return lang.strip().lower().replace('_', '-').replace(' ', '')

def getPreferredLanguages(env):
    '''See interface IUserPreferredLanguages'''
    accept_langs = env.get('HTTP_ACCEPT_LANGUAGE', '').split(',')

    # Normalize lang strings
    accept_langs = [normalize_lang(l) for l in accept_langs]
    # Then filter out empty ones
    accept_langs = [l for l in accept_langs if l]

    accepts = []
    for index, lang in enumerate(accept_langs):
        l = lang.split(';', 2)

        # If not supplied, quality defaults to 1...
        quality = 1.0

        if len(l) == 2:
            q = l[1]
            if q.startswith('q='):
                q = q.split('=', 2)[1]
                quality = float(q)

        if quality == 1.0:
            # ... but we use 1.9 - 0.001 * position to
            # keep the ordering between all items with
            # 1.0 quality, which may include items with no quality
            # defined, and items with quality defined as 1.
            quality = 1.9 - (0.001 * index)

        # we do not use fi-fi type of language... So .split("-")[0] added
        accepts.append((quality, l[0].split("-")[0]))

    # Filter langs with q=0, which means
    # unwanted lang according to the spec
    # See: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4

    return [lang for quality, lang in sorted(accepts, reverse=True)
                if quality and lang in LANGUAGES]

def set_language_cookie(language):
    if language in config.LANGUAGES:
        web.setcookie('I18N_LANGUAGE', language)
        web.ctx.language = language

def get_language_cookie():
    if hasattr(web.ctx, "language"):
        return web.ctx.language
    web_cookies = web.cookies()
    lang = web_cookies.get('I18N_LANGUAGE', '')
    if lang in config.LANGUAGES:
        return lang
    else:
        return ''

# added

def getLanguage():
    if config.show_language_selector:
        lang = get_language_cookie()
        if lang:
            return lang

    if config.LANGUAGE_FORCED:
        return config.LANGUAGE_FORCED

    accepts = getPreferredLanguages(web.ctx.environ)
    try:
        return accepts[0]
    except:
        return LANGUAGES[0]

def fake(s):
    return "#[" + s + "]#"

def _(s, trans_pool={}):
    lang = getLanguage()
    if not trans_pool.has_key(lang):
        trans_pool[lang] = gettext.GNUTranslations(open(LOCALES_DIR % lang))
    return trans_pool[lang].gettext(s)

def n_(s, p, n, trans_pool={}):
    lang = getLanguage()
    if not trans_pool.has_key(lang):
        trans_pool[lang] = gettext.GNUTranslations(open(LOCALES_DIR % lang))
    return trans_pool[lang].ngettext(s, p, n)
