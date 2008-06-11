var map, layer, layer1, layer2;
var point_icon = new OpenLayers.Icon(POINT_ICON_URL, new OpenLayers.Size(POINT_ICON_X, POINT_ICON_Y)),
 new_point_icon = new OpenLayers.Icon(NEW_POINT_ICON_URL, new OpenLayers.Size(NEW_POINT_ICON_X, NEW_POINT_ICON_Y));

var lr;
function remove_layer(){
    map.removeLayer(lr);
    lr = new OpenLayers.Layer("feed");
    map.addLayer(lr)
}
function addol(url){
    if (url.indexOf("?")!=-1) {return url+"&ol=1";}
    else{return url+"?ol=1";};
}
function add_feed1(feed_url){
    lr = new OpenLayers.Layer.GeoRSS("feed", addol(feed_url), {icon:point_icon});
    map.addLayer(lr);
    return lr;
}
function add_feed(feed_url){
    map.removeLayer(lr);
    lr = new OpenLayers.Layer.GeoRSS("feed", addol(feed_url), {icon:point_icon});
    map.addLayer(lr);
    map.setCenter(new OpenLayers.LonLat(lon, lat), 10);
    return lr;
}
function add_feed_z(feed_url){
    map.removeLayer(lr);
    lr = new OpenLayers.Layer.GeoRSS("feed", addol(feed_url), {icon:point_icon});
    map.addLayer(lr);
    map.setCenter(new OpenLayers.LonLat(CENTER_LON, CENTER_LAT), 11);
    return lr;
}
function add_feed_c(feed_url,lat,lon){
    map.removeLayer(lr);
    lr = new OpenLayers.Layer.GeoRSS("feed", addol(feed_url), {icon:point_icon});
    map.addLayer(lr);
    map.setCenter(new OpenLayers.LonLat(lon, lat), 15);
    return lr;
}
function set_newpoint(lat,lon) {
    markersLayer.clearMarkers();
    var marker = new OpenLayers.Marker(
     new OpenLayers.LonLat(lon,lat),
        new_point_icon
    );
    markersLayer.addMarker(marker);
    map.addLayer(markersLayer);        
} 
function ev_handler(e) {
    var lonlat = map.getLonLatFromViewPortPx(e.xy);
    document.getElementById("lon").value = lonlat.lon;
    document.getElementById("lat").value = lonlat.lat;
    set_newpoint(lonlat.lat,lonlat.lon)
}

var markersLayer = new OpenLayers.Layer.Markers("The marker");

function chooseLayer(z, layer, layer1, layer2) {
    if (z > GETMAP_ZOOM2) {
      if(z > GETMAP_ZOOM1){map.setBaseLayer(layer);
      }else{map.setBaseLayer(layer1);
    }
    } else {map.setBaseLayer(layer2);};
};

var zoom_el;


function do_init(){
    map = new OpenLayers.Map('map', MAP_PARAMS);
    if (GETMAP_UNTILED != 0) {
    layer = new OpenLayers.Layer.WMS.Untiled( "OpenLayers WMS",
        GETMAP_URL, {layers: GETMAP_LAYERS}, {isBaseLayer: true,
visibility:true, buffer: 1 } );
    layer1 = new OpenLayers.Layer.WMS.Untiled( "OpenLayers WMS",
        GETMAP_URL, {layers: GETMAP_LAYERS1}, {isBaseLayer: true,
visibility:true, buffer: 1 } );
    layer2 = new OpenLayers.Layer.WMS.Untiled( "OpenLayers WMS",
        GETMAP_URL, {layers: GETMAP_LAYERS2}, {isBaseLayer: true,
visibility:true, buffer: 1 } );
    } else {
    layer = new OpenLayers.Layer.WMS( "OpenLayers WMS",
        GETMAP_URL, {layers: GETMAP_LAYERS}, {isBaseLayer: true,
visibility:true, buffer: 0 } );
    layer1 = new OpenLayers.Layer.WMS( "OpenLayers WMS",
        GETMAP_URL, {layers: GETMAP_LAYERS1}, {isBaseLayer: true,
visibility:true, buffer: 0 } );
    layer2 = new OpenLayers.Layer.WMS( "OpenLayers WMS",
        GETMAP_URL, {layers: GETMAP_LAYERS2}, {isBaseLayer: true,
visibility:true, buffer: 0 } );
}
    map.addLayer(layer);
    map.addLayer(layer1);
    map.addLayer(layer2);

    map.addControl(new OpenLayers.Control.Navigation());
    map.addControl(new OpenLayers.Control.MousePosition());
    panzoombar = new OpenLayers.Control.PanZoomBar();
    // panzoombar.zoomStopWidth = 18,
    // panzoombar.zoomStopHeight = 5,
    map.addControl(panzoombar);
}

function init(){

    if (GETMAP_CUSTOM == "1"){
         custom_init();
    }else{
         do_init();
    };

    // INITIAL_ZOOM = map.getZoomForExtent(new OpenLayers.Bounds(24.82, 60.09, 25.22, 60.3));

    map.setCenter(new OpenLayers.LonLat(CENTER_LON, CENTER_LAT), INITIAL_ZOOM);

    var lon = document.getElementById("lon").value;
    var lat = document.getElementById("lat").value;
    zoom_el = document.getElementById("zoom");
    if (zoom_el) {var zoom=zoom_el.value;} else {var zoom=INITIAL_ZOOM;};

    if (lon != "") {set_newpoint(lat,lon);};

    chooseLayer(zoom, layer, layer1, layer2);

    if (INITIAL_FEED != '') {lr = add_feed1(INITIAL_FEED);}

    if (HAS_NEW_POINT) {
      map.events.register("click", map, function(e){ev_handler(e);});
    }

    map.events.register('zoomend', map,
    	function(e) { 
            chooseLayer(map.zoom, layer, layer1, layer2);
            if (zoom_el) {zoom_el.value = map.zoom;};
            // alert(map.getExtent().toBBOX());
    });

}
function runOnLoad() {init();}
