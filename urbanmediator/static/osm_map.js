function choose_layer(z) {};  //not in use

function custom_init() {
  var options = {
    projection: "EPSG:900913",
    displayProjection: "EPSG:4326",
    units: "m",
    maxResolution: 156543.0339,
    maxExtent: new OpenLayers.Bounds(-20037508, -20037508,
                                     20037508, 20037508.34)
  };

  map = new OpenLayers.Map('map', options);

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
