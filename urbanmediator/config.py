# -*- coding: utf-8 -*-

import os, sha
import web
from DocStorage import FSStorage

########################### Parameters to setup / override

from default_config import *

##########################################################

base_url = "http://localhost:9080"
schema_base_url = base_url + "/Static"

mail_base_domain = "um.uiah.fi"   #!!!

LOCALES_DIR = "locales/%s.mo"
LANGUAGES = ["en", "fi", "es", "ca", "ru"]

db_parameters = dict(dbn='mysql', db='um', user='um', pw='*secret*', use_unicode=False)

###################################### Below experimental overrides

getmap_server = "http://labs.metacarta.com/wms/vmap0?"
getmap_layers = 'basic'
getmap_layers1 = 'basic'
getmap_layers2 = 'basic'
srsname = "EPSG:4326"

########################################################################

middleware = []   # [web.reloader]
cache = True

# storing files
STORAGE_DIR = os.environ["HOME"] + "/.urban_mediator"

file_storage = FSStorage("file://" + STORAGE_DIR, STORAGE_DIR)


instance_dir = os.getcwd()
plugins_dir = os.path.join(instance_dir, "local/packages")
local_docs_dir = os.path.join(instance_dir, "local/docs")
plugins_config = os.path.join(instance_dir, "local/plugins.py")
local_config = os.path.join(instance_dir, "local/config.py")

try:
    execfile(local_config)  # local config overrides
except:
    print "Local config errors!!! (probably missing file)"
    pass

web.config.db_parameters = db_parameters

#web.webapi.internalerror = web.debugerror

session_cookie_name = "um_cookie_" + sha.new(base_url).hexdigest()

if not os.path.exists(STORAGE_DIR):
    os.mkdir(STORAGE_DIR)

# !!! this is a hack to have local plugins on the module path
import sys
sys.path.append(plugins_dir)

del sys, sha, os
