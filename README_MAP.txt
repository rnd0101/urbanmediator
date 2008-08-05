
Setting up the map
------------------

WMS
===

Urban Mediator (UM) uses OpenLayers (OL) as its map portrayal engine.
In order to configure the map, WMS (or other OL compatible map
material) should be available.

Map logic is controlled via the following configuration parameters
(editable by UM instance administrator):

getmap_layers
    (string) name of the most detailed layer

getmap_layers1
    (string) name of the less detailed layer

getmap_layers2
    (string) name of the least detailed layer

getmap_params
    (string) map parameters, JavaScript code, e.g.::

        { maxExtent: 
        new OpenLayers.Bounds(2546000, 6665800, 2568009, 6687009), 
        maxResolution: 5000, units: 'meters', 
        projection: "EPSG:2392", numZoomLevels: 20}

getmap_server
    (string) URL of the server which provides WMS, e.g::
        http://labs.metacarta.com/wms/vmap0?

srsname
    (string) name of the SRS (projection), should be the same as possibly given in getmap_params.

getmap_zoom1
    (int) threshold between most detailed zoom level and less detailed

getmap_zoom2
    (int) threshold between less detailed zoom level and least detailed

with these two parameters, right level is choosen for the right zoom level.
It may require some experimentation to choose zoom levels correctly. 
The best way to experiment is some topic view with the map: it is possible
to set topic zoom level and then play with getmap_zoom1,2 to achieve
best match.

getmap_zoomshift
    (int) configuration parameter which translates
    UM's logical zoom level to OL's zoomlevel. In some cases it is ok
    to be 0, but sometimes it should be less. OL's zoom levels possibly 
    depend on many other parameters (please, refer to OL docs). So,
    this parameter may help to adjust zoom levels especially when UM
    switch one map for another.

topic_zoom
    (int) default topic zoom level. Usually, shoosed to show
    a small distrcit of the city. This zoom level is logical zoom level.

center_lat, center_lon
    (float) coordinates for the city center
    (or district center, if UM is for the district). Coordinate system - WGS84


UM database holds all coordinates in WGS84 internally and translates
coordinates (if necessary) with pyproj library. UM database 
saves only logical zoom levels and translates them to OL zoom levels
by use of getmap_zoomshift parameter. (it may be done more complex
than that in the future).

OSM
===

UM can work with the OpenStreetMap (and other epsg:900913 maps).

In order to enable that, be sure to use pyproj library with the following
additions to the /pyproj/data/epsg file (found in the pyproj)::

    <41001> +proj=merc +lat_ts=0 +lon_0=0 +k=1.000000 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs  no_defs <>
    <900913> +proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs

To use OSM map, UM needs "custom" way of setting up the map. To switch that on,
edit the UM settings (login as admin first)::

    getmap_custom: 1
    getmap_custom_server: http://tah.openstreetmap.org/Tiles/tile/
    getmap_custom_wms: osm
    getmap_zoomshift: 0
    srsname: epsg:900913

and (for example, its possible to make other changes)

getmap_custom_init::

            var options = {
                projection: "EPSG:900913",
                displayProjection: "EPSG:4326",
                units: "m",
                maxResolution: 156543.0339,
                maxExtent: new OpenLayers.Bounds(-20037508, -20037508,
                                                 20037508, 20037508.34)
            };



    map = new OpenLayers.Map('map', options);

            var options = {numZoomLevels: 24};

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



    layer = graphic;
    layer1 = graphic;
    layer2 = graphic;
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


