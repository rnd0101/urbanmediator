var map;
var point_icon, new_point_icon;
var feed_layer, markers_layer;
var zoom_element;

function addol(url){
    if (url.indexOf("?")!=-1) {return url+"&ol=1";}
    else {return url+"?ol=1";};
}
function add_feed_layer(feed_url){
    feed_layer = new OpenLayers.Layer.GeoRSS("feed", addol(feed_url), {icon:point_icon});
    map.addLayer(feed_layer);
    return feed_layer;
}
function set_newpoint(lat,lon) {
    markers_layer.clearMarkers();
    var marker = new OpenLayers.Marker(
     new OpenLayers.LonLat(lon,lat),
        new_point_icon
    );
    markers_layer.addMarker(marker);
    map.addLayer(markers_layer);        
} 
function click_handler(e) {
    var lonlat = map.getLonLatFromViewPortPx(e.xy);
    document.getElementById("lon").value = lonlat.lon;
    document.getElementById("lat").value = lonlat.lat;
    set_newpoint(lonlat.lat,lonlat.lon)
}
function zoomend_handler(e) { 
    choose_layer(map.zoom);
    if (zoom_element) {zoom_element.value = map.zoom;};
    // alert(map.getExtent().toBBOX());
}

function init(){
    point_icon = new OpenLayers.Icon(POINT_ICON_URL, new OpenLayers.Size(POINT_ICON_X, POINT_ICON_Y));
    new_point_icon = new OpenLayers.Icon(NEW_POINT_ICON_URL, new OpenLayers.Size(NEW_POINT_ICON_X, NEW_POINT_ICON_Y));
    markers_layer = new OpenLayers.Layer.Markers("The marker");

    custom_init();

    map.setCenter(new OpenLayers.LonLat(CENTER_LON, CENTER_LAT), INITIAL_ZOOM);

    var lon = document.getElementById("lon").value;
    var lat = document.getElementById("lat").value;
    zoom_element = document.getElementById("zoom");
    if (zoom_element) {var zoom=zoom_element.value;} else {var zoom=INITIAL_ZOOM;};

    if (lon != "") {set_newpoint(lat,lon);};

    choose_layer(zoom);

    if (INITIAL_FEED != '') {feed_layer = add_feed_layer(INITIAL_FEED);}

    if (HAS_NEW_POINT) {
      map.events.register("click", map, click_handler);
    }

    map.events.register('zoomend', map, zoomend_handler);

}
function runOnLoad() {init();}
