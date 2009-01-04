function choose_layer(z) {};  //not in use

function custom_init() {
    var P_LON=2775934.2553;
    var P_LAT=8437870.58044;
    var ext = new OpenLayers.Bounds(P_LON-30, P_LAT-30, P_LON+30, P_LAT+30);
 
    var options = {
        projection: "EPSG:900913",
	units: "m",
	maxResolution: 156543.0339,
	maxExtent: ext
    };

    map = new OpenLayers.Map('map', options);

    var options1 = {numZoomLevels: 3};

    var graphic = new OpenLayers.Layer.Image(
        'Office plan', 'http://some.um.server/media?file_key=94ce2719f8589a1ed1c4e1fcfcfcbf28',
        ext,
        new OpenLayers.Size(64, 48),
        options1);

    map.addLayers([graphic]);
    map.addControl(new OpenLayers.Control.LayerSwitcher());
    map.addControl(new OpenLayers.Control.MousePosition());
    map.zoomToMaxExtent();
}
