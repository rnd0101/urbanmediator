# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Handling mediafiles (stored in the FS)
"""

import md5, mimetypes, time, rfc822, tempfile, StringIO, os, datetime
import web
import Image

import config
from config import file_storage

mimetypes.add_type("video/3gp", ".3gp")
mimetypes.add_type("video/mp4", ".mp4")
mimetypes.add_type("application/vnd.landmarkcollection+xml", ".lmx")

def guess_content_type(filename, default='application/octet-stream'):
    try:
        return mimetypes.guess_type(filename)[0] or default
    except:
        return default

def storeMediaFile(file_contents, prefix=""):
    file_key = md5.new(file_contents).hexdigest()
    file_storage.setItem(prefix + file_key, file_contents)
    return prefix + file_key

def uploadMediaFile(file_contents="", 
                    filename="NotKnown.jpg",
                    content_type=None):
    if file_contents:
        file_key = storeMediaFile(file_contents)
        content_type = content_type or guess_content_type(filename)

        # mostly technical metadata used to show file quickly 
        file_storage.setItem(file_storage.metadata(file_key), 
                         {
                         'Owner': 'NotimplementedYet',
                         'OriginalFilename': filename,   #!!!
                         'Last-Modified': rfc822.formatdate(time.time()),
                         'Content-Type': content_type,   #!!!
                         'Content-Length': str(len(file_contents)),
                         }
                        )
        return "/media?file_key=" + file_key
        # print "FILE SUCCESSFULLY UPLOADED", file_key, len(file_contents)
    else:
        return ""


def uploadMediaFileThumbnail(file_contents="", 
                    filename="NotKnown.jpg",
                    content_type=None,
                    maxx=60, maxy=60):
    """ """
    if file_contents:
        large_file = StringIO.StringIO(file_contents)
        thumb_file = StringIO.StringIO()
        _preview(large_file, thumb_file, maxx=maxx, maxy=maxy)
        file_contents = thumb_file.getvalue()

        return uploadMediaFile(file_contents=file_contents, 
                    filename=filename,
                    content_type="image/jpeg")
    else:
        return ""


# !!! TODO:
# 1. how to find out original filename (web.py know-how)
# 2. add upload form to the site (do not forget enctype attribute!)

def downloadMediaFile(file_key):
    try:
        metadata = file_storage.getItem(file_storage.metadata(file_key))
        web.header('Content-Type', metadata["Content-Type"])
        web.header('Content-Length', str(metadata["Content-Length"]))
        web.header('Last-Modified', metadata["Last-Modified"])
        return file_storage.getItem(file_key, mode="str")
    except KeyError:
        return downloadPreview(file_key)   #??? !!!

def _preview(from_file, to_file, maxx, maxy, ratio=True, angle=0):
    """ Generate a preview using PIL """
    im = Image.open(from_file)
    if im.mode != 'RGB' and im.mode != 'CMYK': 
        im = im.convert('RGB')
    try:
        filter_ = Image.ANTIALIAS
    except AttributeError:
        filter_ = Image.BICUBIC

    if angle != 0:    
        out = im.rotate(angle)
    else:
        out = im
    
    if ratio:               # keep aspect-ratio
        out.thumbnail((maxx, maxy), filter_)
    else:                   # distort to fixed size
        out = out.resize((maxx, maxy), filter_)

    try:
        out.save(to_file, 'JPEG', quality=85)
    except:
        raise

icons = {
  'application': 'icons/application/default.gif',
  'application/msword': 'icons/application/doc.gif',
  'application/pdf': 'icons/application/pdf.gif',
  'application/vnd.ms-powerpoint': 'icons/application/ppt.gif',
  'application/vnd.ms-excel': 'icons/application/xls.gif',
  'application/zip': 'icons/application/zip.gif',
  'application/x-gzip': 'icons/application/zip.gif',
  'application/x-tar': 'icons/application/zip.gif',
  'audio': 'icons/audio/default.gif',
  '': 'icons/default.gif',
  'image': 'icons/image/default.gif',
  'image/vnd.djvu': 'icons/image/djvu.png',
  'text': 'icons/text/default.gif',
  'text/html': 'icons/text/html.gif',
  'text/x-python': 'icons/text/py.gif',
  'text/xml': 'icons/text/xml.gif',
  'video': 'icons/video/default.gif',
  'broken': 'icons/broken.gif',
}


def ct_icon_url(ct):
    try:
        return icons[ct]
    except:
        try:
            return icons[ct.split('/')[0]]
        except:
            return icons['']


def preview_icon(ct):
    return "image/gif", downloadStaticMediaFile(
                    ct_icon_url(ct), config.static_dir, mode="file")

def downloadPreview(file_key, max_x=100, max_y=100):
    if Image is None:
        return
    try:
        metadata = file_storage.getItem(file_storage.metadata(file_key))
        input_file = file_storage.getItem(file_key, mode="file")
        output_file = tempfile.TemporaryFile()

        ratio = 1
        angle = 0

        ct = metadata['Content-Type']
        pre_ct = "image/jpeg"
        if ct.startswith("image/"):
            try:
                _preview(input_file, output_file, max_x, max_y, ratio, angle)
            except:
                pre_ct, output_file = preview_icon(ct)
        else:
            pre_ct, output_file = preview_icon(ct)
        last_modified = metadata["Last-Modified"]
    except:
        pre_ct, output_file = preview_icon('broken')
        last_modified = rfc822.formatdate(time.time())  #!!!?

    output_file.seek(0L, 2)
    preview_length = output_file.tell()
    output_file.seek(0L)
    fc = output_file.read()
    web.header('Content-Type', pre_ct)
    web.header('Content-Length', str(preview_length))
    web.header('Last-Modified', last_modified)
    return fc


def normalize_path(key, base_dir):
        path = os.path.abspath(os.path.join(base_dir, key))
        if not path.startswith(base_dir):
            return "NONEXISTENT"
        return path


def downloadStaticMediaFile(file_key, base_dir, mode="str"):
    path = normalize_path(file_key.rstrip("/"), base_dir)
    try:
        f = open(path, 'rb')
    except IOError:
        web.notfound()
        raise StopIteration

    ctype = guess_content_type(path)
    web.header("Content-type", ctype)
    fs = os.fstat(f.fileno())
    web.header("Content-Length", str(fs[6]))
    web.lastmodified(datetime.datetime.fromtimestamp(fs.st_mtime))
    if mode == "str":
        return f.read()
    elif mode == "file":  
        return f

