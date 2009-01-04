# -*- coding: utf-8 -*-
#
# Default config for the Urban Mediator
# Uses OpenStreetMap

"""

Values to lookup configuration parameters' type and default values.

"""

debug_mode = False
offline_mode = False
rerun = False
default_aging = 10

show_language_selector = True

#mail_base_domain = "example.org"
mail_base_domain = ".+"

topics_per_page = 20
points_per_page = 30
links_per_page = 15
comments_per_page = 20
main_page_elements = "search,tagcloud,hr,add new topic,edit settings,about"
main_page_topic_orders = "recently updated", "newest",  "most points", "title"
main_page_highlighted_order = "title"
main_page_point_orders = "recently updated", "newest",  "oldest", "title", "distance"
point_contributors = "anyone,visitors,registered,topic administrators,nobody"
topic_icons = """topic.icon.info.png 
                 topic.icon.happy.png"""
topic_colours = """A B C"""
max_tags = 64

topic_list_show = "icon,origin,title,topic-description,count-points,latest-description,latest-author,latest-added"

nearby_radius = 200 #m
max_nearby_points = 24

topic_zoom = 15

LANGUAGES = "en", "fi", "es", "nl", "ca", "ru"

LANGUAGE_FORCED = ""

instance_name = dict(en="Urban Mediator",
                     fi="Urban Mediator",
                     es="Urban Mediator",
                     ca="Urban Mediator",
                     ru="Urban Mediator",
                     nl="Urban Mediator",
                    )

instance_name2 = dict(en="-",
                      fi="-",
                      es="-",
                      ca="-",
                      ru="-",
                      nl="-",
                    )

official_icon = "img/icon.official.png"

instance_owner = dict(en="University of Art and Design Helsinki",
                     fi="Taideteollinen korkeakoulu",
                     es="University of Art and Design Helsinki",
                     ca="University of Art and Design Helsinki",
                     ru="University of Art and Design Helsinki",
                     nl="University of Art and Design Helsinki",
                    )

datetime_format = "%d.%m.%Y %H:%M:%S"

origin = ''

center_lat, center_lon = 60.170833, 24.9375   # Helsinki
zoom = 14

mobile_gps_zoom = 15
mobile_zoom = 14
mobile_point_zoom = 16

mobile_map_width = 256
mobile_map_height = 256

disallow_robots = True

show_username_in_point_listing = False

getmap_server = "http://labs.metacarta.com/wms/vmap0?"
getmap_layers = 'basic'
getmap_layers1 = 'basic'
getmap_layers2 = 'basic'
getmap_js = ''

# thresholds for the layer switcher:
getmap_zoom1 = 13
getmap_zoom2 = 12

getmap_custom = 1
getmap_custom_init = """
function choose_layer(z) {};  //not in use

function custom_init() {
  var map_options = {
    projection: "EPSG:900913",
    units: "m",
    maxResolution: 156543.0339,
    maxExtent: new OpenLayers.Bounds(-20037508, -20037508,
                                     20037508, 20037508.34)
  };

  map = new OpenLayers.Map('map', map_options);

  var options = {numZoomLevels: 20};

  // create OSM layer
  var graphic = new OpenLayers.Layer.TMS(
     "OpenStreetMap (Tiles@Home)",
     "http://tah.openstreetmap.org/Tiles/tile/",
     {
       type: 'png', getURL: osm_getTileURL,
       displayOutsideMaxExtent: true,
       attribution: '<a href="http://www.openstreetmap.org/">OpenStreetMap</a>'
     }
  );

  map.addLayers([graphic]);
  map.addControl(new OpenLayers.Control.LayerSwitcher());

  map.addControl(new OpenLayers.Control.MousePosition());
  // map.zoomToMaxExtent();
}

function osm_getTileURL(bounds) {
  var res = this.map.getResolution();
  var x = Math.round((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
  var y = Math.round((this.maxExtent.top - bounds.top) / (res * this.tileSize.h));
  var z = this.map.getZoom();
  var limit = Math.pow(2, z);

  if (y < 0 || y >= limit) {
    return OpenLayers.Util.getImagesLocation() + "404.png";
  } else {
    x = ((x % limit) + limit) % limit;
    return this.url + z + "/" + x + "/" + y + "." + this.type;
  }
};
"""
getmap_custom_wms = "osm"
getmap_custom_server = "http://tah.openstreetmap.org/Tiles/tile/"

getmap_resolutions = "[32,16,8,4,2,1]"

feedback_topic_id = 1
default_user_id_for_mail = 1

getmap_zoomshift = 0

getmap_untiled = 0
use_pyproj = 1

getmap_params = """{ maxResolution: 'auto', numZoomLevels: 20 }"""

getmap_tile_aged_in_cache = 3600*24
# parameter tells how long the tile should be served from cache.
#It can be adjusted according to how dynamic map material is.
#Default is one day.

point_map_zoom = 14.

srsname = "ESRI.extra:900913"

doc_about = dict(en="")
doc_privacy = dict(en="")
doc_contact = dict(en="")
doc_help = dict(en="")
doc_main = dict(en="")
doc_sidenote = dict(en="")
