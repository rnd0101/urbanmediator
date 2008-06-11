# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.
    
    Amended form library from web.py

    HTML forms  (was part of web.py)
    Public Domain
"""

from web.form import *

class Form(Form):
    def __init__(self, *inputs, **kw):
        self.inputs = inputs
        self.valid = True
        self.note = None
        self.validators = kw.pop('validators', [])

    def __call__(self, x=None):
        o = copy.deepcopy(self)
        if x: o.validates(x)
        return o

    def render(self):
        out = ''
        out += self.rendernote(self.note)
        for i in self.inputs:
            if isinstance(i, Fieldset) or isinstance(i, Hidden):
                out += "\n" + i.pre + i.render() + i.post + "\n"
            else:
                cls = i.status()
                if i.sidenote or i.note:
                    out += '<div class="notes" id="note_%s">' % i.id
                    out += '<p class="last">%s %s</p></div>' % (self.rendernote(i.note), i.sidenote)
                out += '<div class="%s"><label for="%s">%s</label>' % (cls, i.id, i.description)
                out += i.pre + i.render() + i.post
                out += "</div>\n"
        return out

    def rendernote(self, note):
        if note: return '<strong class="error">%s</strong>' % note
        else: return ""

    def validates(self, source=None, _validate=True, **kw):
        source = source or kw or web.input()
        out = True
        for i in self.inputs:
            v = attrget(source, i.name)
            if _validate:
                out = i.validate(v) and out
            else:
                i.value = v
        if _validate:
            out = out and self._validate(source)
            self.valid = out
        return out

    def _validate(self, value):
        self.value = value
        for v in self.validators:
            if not v.valid(value):
                self.note = v.msg
                return False
        return True

    def fill(self, source=None, **kw):
        return self.validates(source, _validate=False, **kw)
    
    def __getitem__(self, i):
        for x in self.inputs:
            if x.name == i: return x
        raise KeyError, i
    
    def _get_d(self): #@@ should really be form.attr, no?
        return utils.storage([(i.name, i.value) for i in self.inputs])
    d = property(_get_d)

class Input(object):
    def __init__(self, name, *validators, **attrs):
        self.description = attrs.pop('description', name)
        self.value = attrs.pop('value', None)
        self.pre = attrs.pop('pre', "")
        self.post = attrs.pop('post', "")
        self.sidenote = attrs.pop('sidenote', "")
        self.id = attrs.setdefault('id', name)
        if 'class_' in attrs:
            attrs['class'] = attrs['class_']
            del attrs['class_']
        self.name, self.validators, self.attrs, self.note = name, validators, attrs, None

    def validate(self, value):
        self.value = value
        for v in self.validators:
            if not v.valid(value):
                self.note = v.msg
                return False
        return True

    def status(self):
        for v in self.validators:
            if isinstance(v, FakeValidator):
                return v.msg  # "required"
        return "optional"

    def render(self): raise NotImplementedError

    def addatts(self):
        str = ""
        for (n, v) in self.attrs.items():
            str += ' %s="%s"' % (n, net.websafe(v))
        return str
    
#@@ quoting

class Textbox(Input):
    def render(self):
        x = '<input type="text" name="%s"' % net.websafe(self.name)
        if self.value: x += ' value="%s"' % net.websafe(self.value)
        x += self.addatts()
        x += ' />'
        return x

class Password(Input):
    def render(self):
        x = '<input type="password" name="%s"' % net.websafe(self.name)
        if self.value: x += ' value="%s"' % net.websafe(self.value)
        x += self.addatts()
        x += ' />'
        return x

class Textarea(Input):
    def render(self):
        x = '<textarea name="%s"' % net.websafe(self.name)
        x += self.addatts()
        x += '>'
        if self.value is not None: x += net.websafe(self.value)
        x += '</textarea>'
        return x

class Dropdown(Input):
    def __init__(self, name, args, *validators, **attrs):
        self.args = args
        super(Dropdown, self).__init__(name, *validators, **attrs)

    def render(self):
        x = '<select name="%s"%s>\n' % (net.websafe(self.name), self.addatts())
        for arg in self.args:
            if type(arg) == tuple:
                value, desc= arg
            else:
                value, desc = arg, arg 

            if self.value == value: select_p = ' selected="selected"'
            else: select_p = ''
            x += '  <option %s value="%s">%s</option>\n' % (select_p, net.websafe(value), net.websafe(desc))
        x += '</select>\n'
        return x

class Radio(Input):
    def __init__(self, name, args, *validators, **attrs):
        self.args = args
        super(Radio, self).__init__(name, *validators, **attrs)

    def render(self):
        x = '<span>'
        for arg in self.args:
            if self.value == arg: select_p = ' checked="checked"'
            else: select_p = ''
            x += '<input type="radio" name="%s" value="%s"%s%s /> %s ' % (net.websafe(self.name), net.websafe(arg), select_p, self.addatts(), net.websafe(arg))
        return x+'</span>'

class Checkbox(Input):
    def render(self):
        x = '<input name="%s" type="checkbox"' % net.websafe(self.name)
        if self.value: x += ' checked="checked"'
        x += self.addatts()
        x += ' />'
        return x

class Button(Input):
    def __init__(self, name, *validators, **attrs):
        super(Button, self).__init__(name, *validators, **attrs)
        self.description = ""

    def render(self):
        safename = net.websafe(self.name)
        x = '<button name="%s"%s>%s</button>' % (safename, self.addatts(), safename)
        return x

class Fieldset(Input):
    def __init__(self, name, *validators, **attrs):
        super(Fieldset, self).__init__(name, *validators, **attrs)

    def render(self):
        if self.name == "end_of_fieldset":
            x = '</fieldset>'
        else:
            x = '<fieldset%s>' % self.addatts()
            x += '<legend>%s</legend>' % self.description
        return x

class Raw(Input):
    def __init__(self, name, *validators, **attrs):
        super(Raw, self).__init__(name, *validators, **attrs)

    def render(self):
        return ""

class Hidden(Input):
    def __init__(self, name, *validators, **attrs):
        super(Hidden, self).__init__(name, *validators, **attrs)
        # it doesnt make sence for a hidden field to have description
        self.description = ""

    def render(self):
        x = '<input type="hidden" name="%s"%s ' % (net.websafe(self.name), self.addatts())
        if self.value: x += ' value="%s"' % net.websafe(self.value)
        x += ' />'
        return x

class File(Input):
    def render(self):
        x = '<input type="file" name="%s"' % net.websafe(self.name)
        x += self.addatts()
        x += ' />'
        return x
    
class Validator:
    def __deepcopy__(self, memo): return copy.copy(self)
    def __init__(self, msg, test, jstest=None): utils.autoassign(self, locals())
    def valid(self, value): 
        try: return self.test(value)
        except: return False

class Editor(Textarea):
    def render(self):
        import fckeditor, view, links, i18n
        sBasePath = links.pc_links.fckeditor_base
        oFCKeditor = fckeditor.FCKeditor(self.name)
        oFCKeditor.BasePath = sBasePath
        oFCKeditor.Value = view.render_text(self.value or "")
        oFCKeditor.Config = {"CustomConfigurationsPath": 
            links.pc_links("editor_base_url", 
                AutoDetectLanguage="false",
                DefaultLanguage=i18n.getLanguage())
            }
        return oFCKeditor.Create()


notnull = Validator("Required", bool)

class FakeValidator(Validator):
    def valid(self, value): 
        return True

required = FakeValidator("required", None)
required_wide = FakeValidator("required wide", None)
optional = FakeValidator("optional", None)

class regexp(Validator):
    def __init__(self, rexp, msg):
        self.rexp = re.compile(rexp)
        self.msg = msg
    
    def valid(self, value):
        return bool(self.rexp.match(value))
