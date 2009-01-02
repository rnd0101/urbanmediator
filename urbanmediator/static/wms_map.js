
var layer, layer1, layer2;

function choose_layer(z) {
    if (z > GETMAP_ZOOM2) {
      if(z > GETMAP_ZOOM1){map.setBaseLayer(layer);
      }else{map.setBaseLayer(layer1);
    }
    } else {map.setBaseLayer(layer2);};
};

function custom_init(){
    map = new OpenLayers.Map('map', MAP_PARAMS);
    if (GETMAP_UNTILED != 0) {
      var opt = {isBaseLayer: true, visibility:true, buffer: 1} 
      layer = new OpenLayers.Layer.WMS.Untiled( "OpenLayers WMS",
        GETMAP_URL, {layers: GETMAP_LAYERS}, opt);
      layer1 = new OpenLayers.Layer.WMS.Untiled( "OpenLayers WMS",
        GETMAP_URL, {layers: GETMAP_LAYERS1}, opt);
      layer2 = new OpenLayers.Layer.WMS.Untiled( "OpenLayers WMS",
        GETMAP_URL, {layers: GETMAP_LAYERS2}, opt);
    } else {
      var opt = {isBaseLayer: true, visibility:true, buffer: 0} 
      layer = new OpenLayers.Layer.WMS( "OpenLayers WMS",
        GETMAP_URL, {layers: GETMAP_LAYERS}, opt);
    layer1 = new OpenLayers.Layer.WMS( "OpenLayers WMS",
        GETMAP_URL, {layers: GETMAP_LAYERS1}, opt);
    layer2 = new OpenLayers.Layer.WMS( "OpenLayers WMS",
        GETMAP_URL, {layers: GETMAP_LAYERS2}, opt);
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
