# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Handling UM's captchas.
"""

import md5, mimetypes, time, rfc822, tempfile, StringIO, random, re

import PIL.Image as Image
import PIL.ImageFont as ImageFont
import PIL.ImageDraw as ImageDraw
import PIL.ImageFilter as ImageFilter

import web

from config import file_storage

CAPTCHA_PREFIX = "CAPTCHAS/"

goodkey_re = re.compile("^" + CAPTCHA_PREFIX + "[a-fA-F0-9]+$")

# Based on:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/440588

def _gen_captcha(text, fnt, fnt_sz):
    """Generate a captcha image"""
    # randomly select the foreground color
    fgcolor = random.randint(0,0xffff00)
    # make the background color the opposite of fgcolor
    bgcolor = fgcolor ^ 0xffffff
    # create a font object 
    font = ImageFont.truetype(fnt,fnt_sz)
    # determine dimensions of the text
    dim = font.getsize(text)
    # create a new image slightly larger that the text
    im = Image.new('RGB', (dim[0]+5,dim[1]+5), bgcolor)
    d = ImageDraw.Draw(im)
    x, y = im.size
    r = random.randint
    # draw 100 random colored boxes on the background
    for num in range(20):
        d.rectangle((r(0,x),r(0,y),r(0,x),r(0,y)),fill=r(0,0xffffff))
    # add the text to the image
    d.text((3,3), text, font=font, fill=fgcolor)
    im = im.filter(ImageFilter.EDGE_ENHANCE_MORE)
    # save the image to a file
    out_file = StringIO.StringIO()
    im.save(out_file, format='JPEG')
    return out_file.getvalue()

def new_captcha():
    secret_word = str(random.randint(10000, 99999))
    captcha_image = _gen_captcha(secret_word, 'freefont.ttf', 30)
    captcha_key = _upload_captcha(captcha_image, secret_word)
    return captcha_key

def drop_captcha(file_key):
    try:
        if goodkey_re.match(file_key):
            file_storage.delItem(file_key)  
    except:
        pass

def check_captcha(file_key, user_word):
    if not goodkey_re.match(file_key):
        return "Invalid key format"
    try:
        metadata = file_storage.getItem(file_storage.metadata(file_key))
    except:
        return "No such thing"
    try:
        if time.time() - metadata["added"] > 180:   # captcha is too old
            return "Too old"
        if user_word.strip() == metadata["secret"]:
            return ""
    finally:
        drop_captcha(file_key)  
    return "Failed"

def _upload_captcha(file_contents,
                   secret_word,
                   filename="NotKnown.jpg"):
    file_key = CAPTCHA_PREFIX + md5.new(file_contents).hexdigest()
    file_storage.setItem(file_key, file_contents)
    content_type = mimetypes.guess_type(filename)[0]

    # mostly technical metadata used to show file quickly 
    file_storage.setItem(file_storage.metadata(file_key), 
                         {
                         'Owner': 'NotimplementedYet',
                         'secret': secret_word, 
                         'added': time.time(), 
                         'OriginalFilename': filename,   #!!!
                         'Last-Modified': rfc822.formatdate(time.time()),
                         'Content-Type': content_type,   #!!!
                         'Content-Length': len(file_contents),
                         }
                        )
    return file_key

def download_captcha(file_key):
    if not goodkey_re.match(file_key):
        return
    metadata = file_storage.getItem(file_storage.metadata(file_key))
    web.header('Content-Type', metadata["Content-Type"])
    web.header('Content-Length', str(metadata["Content-Length"]))
    web.header('Last-Modified', metadata["Last-Modified"])
    return file_storage.getItem(file_key, mode="str")


if __name__ == '__main__':
    word = str(random.randint(10000, 99999))
    gen_captcha(word.strip(), 'freefont.ttf', 30, "test.jpg")
