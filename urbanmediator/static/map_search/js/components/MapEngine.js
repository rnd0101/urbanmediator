function init()
{	
	//Create the map
	var map_engine 	= new MapEngine();
	map_engine.doSearch();	

}

function MapEngine()
{                
	// SETTING CONFIG VARIABLES
	this.proxy_url = JSON_URL;
	this.search_url = FORM_ACTION;
	this.marker_image_url = MARKER_URL;
	this.search_tags_parameter = SEARCH_TAGS_PARAM;

	//this.init();
	this.initialized = false;

	//NOTE!
	
		//Replacable strings in templates
  		//<!--replace_point_id-->		
  		//<!--replace_point_name-->		
  		//<!--replace_date_creation-->		
  		//<!--replace_href_point_page-->	
  		//<!--replace_lon-->	
  		//<!--replace_lat-->							
  		//<!--replace_creator_user_name-->
  		//<!--replace_creator_user_id-->
  		//<!--replace_content_text-->	
  		//<!--replace_content_images-->	
  		//<!--replace_tags-->	

	//Proxy url / um data url
	this.um_url = this.proxy_url;

	//Messages
	this.msg_no_search_results = "<p class=\"msg_no_results\">Your search gave 0 results.</p>";
	

	//Templates
	
		//MARKER POPUP
		this.popup_template 	= 	"<div class=\"map_popup_container\">";
		this.popup_template 	+=  "<h3 class=\"map_popup_title\"><!--replace_point_name--></h3>";
		this.popup_template 	+=  "</div>";		

		//LIST OF POINTS BLOCK
		this.lop_template 	= 	"<div id=\"lop_<!--replace_point_id-->\" class=\"lop_block\">";
		this.lop_template 	+=	"	<p class=\"lop_point_name\"><!--replace_point_name--></p>";
		this.lop_template 	+=	"	<div id=\"lop_data_<!--replace_point_id-->\" class=\"lop_block_data\"><br />";
		this.lop_template 	+=	"		<p class=\"lop_point_description\"><!--replace_content_text--></p><br />";
		this.lop_template 	+=	"		<p class=\"lop_point_metadata\"><!--replace_creator_user_name--></p>";
		this.lop_template 	+=	"		<p class=\"lop_point_metadata\"><!--replace_date_creation--></p><br />";
		this.lop_template 	+=	"		<p class=\"lop_point_metadata\"><!--replace_tags--></p><br />";
		this.lop_template 	+=	"		<p class=\"lop_point_metadata\"><a target=\"_blank\" class=\"lop_link_to_point_page\" href=\"<!--replace_href_point_page-->\">Go to the point page</a></p>";		
		this.lop_template 	+=	"		<br />";
		this.lop_template 	+= 	"	</div>";
		this.lop_template 	+= 	"</div>";
	
		//SEARCH FORM
		this.search_form_template  	= 	"<form id=\"searchform\" action=\"" + this.search_url + "\" method=\"get\"><div style=\"width: 100%; height: 16px;\"><!--empty--></div>";
		this.search_form_template  	+= 	"<input type=\"text\" name=\"search\" class=\"search-text-input\" id=\"search-text-map\" value=\"<!--search_words-->\" /><input id=\"search-button\" type=\"image\" src=\"static/img/search_send_form.jpg\" alt=\"Search\"><br /><br />";
		this.search_form_template  	+= 	"<input type=\"radio\" name=\"search_tags\" id=\"searchtype_tags\" value=\"true\" checked=\"checked\" />tags&nbsp;&nbsp;";
		this.search_form_template  	+= 	"<input type=\"radio\" name=\"search_tags\" id=\"searchtype_text\" value=\"false\" />all text";
		this.search_form_template  	+= 	"</form>";
	
	//OpenLayers Map variables
	this.map			=	null;
	this.map_options 	=  MAP_PARAMS;
// { resolutions: [32, 16, 8, 4, 2, 1], units: "meters", projection: "EPSG:2392",  maxExtent: new OpenLayers.Bounds(2546000, 6665800, 2568009, 6687009) };

	//Layers (different maps)
	this.wms_layers 		= new Array();
	this.wms_layers[1] 		= new OpenLayers.Layer.WMS( "Map 1", GETMAP_URL, {layers: GETMAP_LAYERS2} );			
	this.wms_layers[2] 		= new OpenLayers.Layer.WMS( "Map 2", GETMAP_URL, {layers: GETMAP_LAYERS1} );		
	this.wms_layers[3] 		= new OpenLayers.Layer.WMS( "Map 3", GETMAP_URL, {layers: GETMAP_LAYERS} );
           
    //Start values for center
    this.center_coord_x_initial = CENTER_LON;
    this.center_coord_y_initial = CENTER_LAT;
        
    this.zoomlevel_initial		= INITIAL_ZOOM;
                 
	//Icon data
 	this.icon_size 			= new OpenLayers.Size(21,28);
	this.icon_offset 		= new OpenLayers.Pixel(-(this.icon_size.w/2), -this.icon_size.h);
	this.icon				= new OpenLayers.Icon(this.marker_image_url, this.icon_size, this.icon_offset);

	//Popup data
	this.popup_offset		= this.icon_offset;
 	this.popup_size_default = new OpenLayers.Size(150,20);
   	
   	//Query string object
   	this.query_string = new Object();

	//Markers array
	this.markers		= new Array();

	//Topics array
	this.topics			= new Array();
	
	//Variables to know if marker or lop is clicked ON
	this.marker_on 		= null;
	this.lop_on 		= null;
	
	//Variables to store topics and chosen topics
	this.topics 		= new Array();
	this.chosen_topics 	= new Array();
	
	//Points list for the Json engine
	this.points_list 	= new Object();
	
	//Avoid Javascript's this -confusion
	var self = this;


//----------------------------------------------------------------------------------------------------------------

	this.showRightMap = function()
	{
		if(self.map.getZoom() == 0)	{ self.map.setBaseLayer(self.wms_layers[1]); }
		if(self.map.getZoom() == 1)	{ self.map.setBaseLayer(self.wms_layers[1]); }
		if(self.map.getZoom() == 2)	{ self.map.setBaseLayer(self.wms_layers[2]); }
		if(self.map.getZoom() == 3)	{ self.map.setBaseLayer(self.wms_layers[2]); }
		if(self.map.getZoom() == 4)	{ self.map.setBaseLayer(self.wms_layers[3]); }			
		if(self.map.getZoom() == 5)	{ self.map.setBaseLayer(self.wms_layers[3]); }	
				
	}

	this.addPoints = function() 
	{
		//Create help variables
		var marker 					= null;
		var point_location 			= null;
		var popup_location 			= null;		
		var point_info 				= null;
		
		//Check map size in coordinates
		//var bounds = self.map.calculateBounds();

		//Create layer for markers
		var marker_layer 	= new OpenLayers.Layer.Markers("Search results");
		marker_layer.name 	= "markers_layer";

		if(self.points_list.is_empty == false)
		{
			//Iterate through points list
			for(var point_id in self.points_list.list)
			{		
				point_info 	= self.points_list.list[point_id];
			
				//Create list of topics
				for(topic_id_tmp in point_info["topics"])
				{
					var topic_id = point_info["topics"][topic_id_tmp]["topic_id"];
					if(self.checkIfTopicOnList(topic_id) == false)
					{
						//If the topic doesn't exist on the list, add it as an topic object
						var temp_object = new Object();
						temp_object.id_topic 	= point_info["topics"][topic_id_tmp]["topic_id"];
						temp_object.name_topic 	= point_info["topics"][topic_id_tmp]["topic_name"];
						temp_object.href_topic 	= point_info["topics"][topic_id_tmp]["href_topic_page"];
						self.topics.push(temp_object);										
					}
				}
						
				//Basic marker data
				point_location					= new OpenLayers.LonLat(point_info["info"]["lon"], point_info["info"]["lat"]);
				marker							= new OpenLayers.Marker(point_location, self.icon.clone());
				marker.id						= point_info["info"]["point_id"];
				marker.descr					= point_info["content"]["textual"];
				marker.topics					= point_info["topics"];
				marker.info						= point_info["info"];
				marker.content					= point_info["content"];
				marker.tags						= point_info["tags"];												
            	marker.icon.imageDiv.className 	= "markerDiv";	//For hovering and expanding		
            	marker.amount_hidden_topics		= 0;
		
				//Create popup for the marker
				popup_location			= new OpenLayers.LonLat(point_info["info"]["lon"], point_info["info"]["lat"]);
				popup 					= new OpenLayers.Popup(point_info["info"]["point_id"], popup_location, self.popup_size_default, point_info["popup_pre"]);
				popup.opacity			= 1.0;
				marker.popup 			= popup;

				// LISTENERS FOR MAP MARKERS
				marker.events.register('mouseover', 		marker, self.markerHover);
				marker.events.register('mouseout', 			marker, self.markerDeHover); 
				marker.events.register('click', 			marker, self.markerClick);
			
				//Add marker to a marker -layer
				marker_layer.addMarker(marker);
			}
		}
		else
		{
			//No points from database / search
		}
		
		//Create the map
        self.map = new OpenLayers.Map( $('map') , self.map_options);

        self.map.addControl(new OpenLayers.Control.Navigation());
        self.map.addControl(new OpenLayers.Control.MousePosition());
        self.map.addControl(new OpenLayers.Control.PanZoomBar());

        //Add the markers layer		
    	self.map.addLayer(marker_layer); 		
        	
        //Set initial values
        self.map.addLayer(self.wms_layers[1]);
        self.map.addLayer(self.wms_layers[2]);
        self.map.addLayer(self.wms_layers[3]);
 
 		self.map.layers[0].setVisibility(true);		
		self.map.layers[1].setVisibility(true);	
		self.map.layers[2].setVisibility(true);	
                
         //Set the center of the map
         self.map.setCenter(new OpenLayers.LonLat(self.center_coord_x_initial, self.center_coord_y_initial));
						    		
    	//Register zoomend event for the map (update the list of points)
    	self.map.events.register("zoomend", self.map, this.zoomEnd);
    		
    	//Register moveend event for the map (update the list of points)
    	self.map.events.register("moveend", self.map, this.moveEnd);	
		
		//TEMP : Layer switcher
		//self.map.addControl(new OpenLayers.Control.LayerSwitcher({'ascending':false}));
		
		//ZOOM TO EXTENT THAT SHOWS ALL THE POINTS (if there are any)
		if(self.points_list.is_empty == true)
		{
			//No points, zoom to default map size
			self.map.zoomTo(self.zoomlevel_initial);
		}
		else
		{
			//Zoom to bounds
			self.map.zoomToExtent(self.points_list.bounds);
		}		
		
		self.showRightMap();

		//Update the list of topics
		self.updateTopicList();

		//Update the list of points
    	self.updateLOP();		
    	
    	//Create the search form
    	var param_search 	= "";
    	var param_tags 		= "";
    	self.createSearchForm();
    	
    	//Set initialized -flag
    	self.initialized = true;
	}
	
	this.createSearchForm = function()
	{
		var template = self.search_form_template.replace(/<!--search_words-->/g, self.query_string.search);
		document.getElementById("searchform").innerHTML = template;
	}
	
	this.getMarkersLayer = function()
	{
		for (layer_id in self.map.layers)
		{
			var temp_layer = self.map.layers[layer_id];
			if(temp_layer.name == "markers_layer")
			{
				var mlayer = temp_layer;
			}
		}
		
		return mlayer;
	}
	
	this.updateLOP = function()
	{
		if(self.points_list.is_empty == false)
		{
			var marker 	= null;
			var lop 	= "";
			var point	= null;
		
			var mlayer = self.getMarkersLayer();
								
				//Create the list of points
				for(var marker_id in mlayer.markers)
				{
					marker = mlayer.markers[marker_id];
					
					if(self.checkIfMarkerOnMapArea(marker) == true && marker.amount_hidden_topics != marker.topics.length)
					{
						point = self.getPointFromListById(marker.id);
						lop += self.formatLOPBlock(point);
					}
				}
			

				document.getElementById("list_of_points").innerHTML = lop;
				
				//Create event listeners and keep possibly opened lop -element open	
				var lop_element 	= null;
				self.lop_on  		= null;
			
				for(var marker_id in mlayer.markers)
				{
					marker = mlayer.markers[marker_id];					
					if(self.checkIfMarkerOnMapArea(marker) == true && marker.amount_hidden_topics != marker.topics.length)
					{

						lop_element = document.getElementById("lop_" + marker.id);
				
						// LISTENERS FOR POINT LIST
						lop_element.addEventListener("mouseover", self.lopHover, true);
						lop_element.addEventListener("mouseout", self.lopDeHover, true);
						lop_element.addEventListener("click", self.lopClick, true);
					
						//Open lop element check
						if(self.marker_on != null)
						{
							if(lop_element.id == ("lop_" + self.marker_on.id))
							{
								self.clickLop(lop_element, "function");
							}
						}
					}					
				}
		}
		else
		{
			document.getElementById("list_of_points").innerHTML = self.msg_no_search_results;
		}

	}
	
	this.updateTopicList = function()
	{
		
		if(self.topics.length > 0)
		{
			//Layer filter checkboxes		
			var checkboxes = "";
		
			for(var id in self.topics)
			{
				checkboxes += "<div class=\"topics_checkbox\"><p class=\"p_topics_checkbox\"><input type=\"checkbox\" id=\"topic_filter_" + self.topics[id].id_topic + "\" checked=\"checked\">&nbsp;<a target=\"_blank\" href=\"" + self.topics[id].href_topic  + "\">" + self.topics[id].name_topic + "</a></p></li>";
			}
			document.getElementById("topiclist").innerHTML = checkboxes;

			//Checkbox event listeners
			var temp = null;
			for(var id in self.topics)
			{
				temp = document.getElementById("topic_filter_" + self.topics[id].id_topic);
				temp.addEventListener("click", self.layersShowHide, false);		
			}
		}
		else
		{
			document.getElementById("topiclist").innerHTML = "";
		}


	}	

	this.layersShowHide = function(evt)
	{		
		
		var current_topic_id = this.id.substring(13, this.id.length);
		
		if(this.checked == true)
		{
			self.markTopicsToBeShown(current_topic_id);			
		}
		else
		{
			self.markTopicsToBeHidden(current_topic_id);
		}
		
		//Update views
		self.updateViews();
	}

	this.updateViews = function()
	{
		var mlayer = self.getMarkersLayer();
				
		//For each marker
		for(marker_id in mlayer.markers)
		{
			var marker = mlayer.markers[marker_id];
			
			if(marker.amount_hidden_topics == marker.topics.length)
			{
				//Hide
				if(document.getElementById("lop_" + marker.id))
				{

					var lop_elem_temp = document.getElementById("lop_" + marker.id)
					self.clearLop(lop_elem_temp);
					document.getElementById("lop_" + marker.id).style.visibility = "collapse";										
				}
				marker.display(false);
				
				self.clearMarker(marker);
			}
			else
			{
				//Show
				if(document.getElementById("lop_" + marker.id))
				{				
					document.getElementById("lop_" + marker.id).style.visibility = "visible";
				}
				marker.display(true);
			}

		}		
	}
	
	this.markTopicsToBeHidden = function(current_topic_id)
	{
		var mlayer = self.getMarkersLayer();		
		
		//For each marker
		for(marker_id in mlayer.markers)
		{
			var marker = mlayer.markers[marker_id];
			
			//For each topic of the marker
			for(topic_id_tmp in marker.topics)
			{
				var topic = marker.topics[topic_id_tmp];
				if(topic.topic_id == current_topic_id)
				{
					//Mark a topic hidden
					marker.amount_hidden_topics++;
				}
			}
		}		
	}
	
	this.markTopicsToBeShown = function(current_topic_id)
	{
		var mlayer = self.getMarkersLayer();		
		
		//For each marker
		for(marker_id in mlayer.markers)
		{
			var marker = mlayer.markers[marker_id];
			
			//For each topic of the marker
			for(topic_id_tmp in marker.topics)
			{
				var topic = marker.topics[topic_id_tmp];
				if(topic.topic_id == current_topic_id)
				{
					//Mark a topic hidden
					marker.amount_hidden_topics--;
				}
			}
		}		
	}	

	this.checkIfTopicOnList = function(id)
	{
		for(topic_id in self.topics)
		{
			var topic = self.topics[topic_id];
			if(topic.id_topic == id)
			{
				return true;
				break;
			}
		}
		return false;				
	}

	this.getMarkerFromListById = function(id)
	{
		var mlayer = self.getMarkersLayer();
		for(var point_id in mlayer.markers)
		{
			if(mlayer.markers[point_id].id == id)
			{
				return mlayer.markers[point_id];
				break;
			}
		}
		return false;				
	}

	this.getPointFromListById = function(id)
	{
		for(var point_id in self.points_list.list)
		{
			if(self.points_list.list[point_id].info.point_id == id)
			{
				return self.points_list.list[point_id];
				break;
			}
		}
		return false;
	}

	this.checkIfMarkerOnMapArea = function(marker)
	{
		var bounds 	= self.map.calculateBounds();
		var ret_val = false;
		
		if(marker.lonlat.lon > bounds.left && marker.lonlat.lon < bounds.right && marker.lonlat.lat < bounds.top &&  marker.lonlat.lat > bounds.bottom)
		{
			ret_val = true;
		}
		
		return ret_val;
	}

	this.formatLOPBlock = function(point_info)
	{
			var formatted = "";
			
			//Create popup layout
			var info 		= point_info.info;
			var content 	= point_info.content;
			
			//Info
			var lop_template = self.lop_template.replace(/<!--replace_point_id-->/g, 	info["point_id"]);
			lop_template = lop_template.replace(/<!--replace_point_name-->/g, 			info["point_name"]);			
			lop_template = lop_template.replace(/<!--replace_date_creation-->/g, 		info["date_creation"]);			
			lop_template = lop_template.replace(/<!--replace_href_point_page-->/g, 		info["href_point_page"]);	
			lop_template = lop_template.replace(/<!--replace_lon-->/g, 					info["lon"]);	
			lop_template = lop_template.replace(/<!--replace_lat-->/g, 					info["lat"]);							
			lop_template = lop_template.replace(/<!--replace_creator_user_name-->/g, 	info["creator_user_name"]);	
			lop_template = lop_template.replace(/<!--replace_creator_user_id-->/g, 		info["creator_user_id"]);	
			
			//Content
			lop_template = lop_template.replace(/<!--replace_content_text-->/g, 		content["textual"]);	
			
			//Tags
			var tags = "";
			if(point_info.tags)
			{
				tags += "Tags<br />";
				for (tag_id in point_info.tags)
				{
					tags += "<a class=\"lop_tags\" href=\"" + this.search_url + "?search_tags=true&search=" + point_info.tags[tag_id] + "\">" + point_info.tags[tag_id] + "</a> ";
				}
			}
			else
			{
				tags += "No tags";
			}	
			
			lop_template = lop_template.replace(/<!--replace_tags-->/g, tags);	
						
			formatted = lop_template;	
			return formatted;			
	}

//----------------------------------------------------------------------------------------------------------------

	//Dispatch
	this.markerHover 	= function(evt) { self.hoverMarker(this, "marker"); }
	this.markerDeHover 	= function(evt) { self.deHoverMarker(this, "marker"); }
	this.markerClick 	= function(evt) { self.clickMarker(this, "marker"); }

	this.lopHover 	= function(evt) { self.hoverLop(this, "lop"); }
	this.lopDeHover = function(evt) { self.deHoverLop(this, "lop"); }
	this.lopClick 	= function(evt) { self.clickLop(this, "lop"); }
	
	this.zoomEnd 	= function(evt) { if(self.initialized == true) { self.updateLOP(); self.showRightMap(); }}
	this.moveEnd 	= function(evt) { if(self.initialized == true) { self.updateLOP(); self.showRightMap(); }}
	
	//Handlers
	this.hoverMarker = function(obj, from)
	{
		if(from == "marker")
		{
			//Hover marker
			if(obj.popup_exists != true)
			{
				obj.popup_exists = true;
				self.map.addPopup(obj.popup);
			}
			
			//Hover lop
			var temp_obj = document.getElementById("lop_" + obj.id);
			self.hoverLop(temp_obj, "marker");	
		}
		else
		{
			//Hover marker
			if(obj.popup_exists != true)
			{
				obj.popup_exists = true;
				self.map.addPopup(obj.popup);
			}
		}
	}

	this.deHoverMarker = function(obj, from)
	{
		if(from == "marker")
		{		
			//Dehover marker
			if(obj.popup_exists != false && self.marker_on != obj)
			{
				obj.popup_exists = false;
				self.map.removePopup(obj.popup);
			}
			
			//Dehover lop
			var temp_obj = document.getElementById("lop_" + obj.id);
			self.deHoverLop(temp_obj, "marker");				
		}
		else
		{
			//Dehover marker
			if(obj.popup_exists != false && self.marker_on != obj)
			{
				obj.popup_exists = false;
				self.map.removePopup(obj.popup);
			}			
		}
	}
	
	this.clickMarker = function(obj, from)
	{
		if(from == "marker")
		{
			if(self.marker_on != obj)
			{
				//Turn popup ON
				if(self.marker_on != null)
				{ 
					this.clearMarker(self.marker_on, "marker");
				}
				self.marker_on 			= obj;
				obj.popup.div.className	= "olPopupChosen";
				
				//Turn lop ON
				var temp_element = document.getElementById("lop_" + obj.id);
				self.clickLop(temp_element, "marker");
			}
			else
			{
				//Turn popup OFF	
				self.marker_on 	= null;
				obj.popup.div.className 	= "olPopup";	
				
				//Turn lop OFF
				var temp_element = document.getElementById("lop_" + obj.id);
				self.clickLop(temp_element, "marker");								
			}
		}
		else
		{
			if(self.marker_on != obj)
			{
				//Turn popup ON
				if(self.marker_on != null)
				{ 
					this.clearMarker(self.marker_on, "marker");
				}
				self.marker_on 			= obj;
				obj.popup.div.className	= "olPopupChosen";
			}
			else
			{
				//Turn popup OFF	
				self.marker_on 	= null;
				obj.popup.div.className 	= "olPopup";								
			}
			
		}
	}
	
	this.clearMarker = function(obj, from)
	{
		obj.popup_exists 				= false;
		obj.popup.div.className 		= "olPopup";	
		self.map.removePopup(obj.popup);
	}	


	this.hoverLop = function(obj, from)
	{ 
		if(self.lop_on != obj)
		{
			if(from == "lop")
			{
				//Hover data
				obj.className = "lop_block_hover";
			
				//Hover marker
				var temp_id 	= obj.id.substring(4, (obj.id.length));
				var temp_marker = self.getMarkerFromListById(temp_id);
				self.hoverMarker(temp_marker, "lop");
			}
			else
			{
				//Hoverdata
				obj.className = "lop_block_hover";			
			}
		}
	}

	this.deHoverLop = function(obj, from)
	{
		if(self.lop_on != obj)
		{		
			if(from == "lop")
			{		
				//Dehover data			
				obj.className = "lop_block";

				//Dehover marker
				var temp_id 	= obj.id.substring(4, (obj.id.length));
				var temp_marker = self.getMarkerFromListById(temp_id);
				self.deHoverMarker(temp_marker, "lop");	
			}
			else
			{
				//Dehover data			
				obj.className = "lop_block";			
			}
		}
	}
	
	this.clickLop = function(obj, from)
	{
		if(from == "lop")
		{
			if(self.lop_on != obj)
			{
				//Turn lop ON
				if(self.lop_on != null)
				{	 
					this.clearLop(self.lop_on);
				}
				
				self.lop_on = obj;
				var temp = "lop_data_" + obj.id.substring(4, (obj.id.length));
				document.getElementById(temp).className	= "lop_block_data_clicked";
				obj.className = "lop_block_on";
				
				//Turn popup ON	
				var temp_id 	= obj.id.substring(4, (obj.id.length));
				var temp_marker = self.getMarkerFromListById(temp_id);				
				self.clickMarker(temp_marker, "lop");
			}
			else
			{
				//Turn lop OFF
				self.lop_on = null;
				var temp = "lop_data_" + obj.id.substring(4, (obj.id.length));
				document.getElementById(temp).className	= "lop_block_data";
				obj.className = "lop_block";
				
				//Turn popup OFF
				var temp_id 	= obj.id.substring(4, (obj.id.length));
				var temp_marker = self.getMarkerFromListById(temp_id);				
				self.clickMarker(temp_marker, "lop");							
			}			
		}
		else
		{
			if(self.lop_on == null)
			{
				//Turn lop ON
				if(self.lop_on != null)
				{	 
					this.clearLop(self.lop_on);
				}
				
				self.lop_on = obj;
				var temp = "lop_data_" + obj.id.substring(4, (obj.id.length));
				document.getElementById(temp).className	= "lop_block_data_clicked";
				obj.className = "lop_block_on";				
			}
			else if(self.lop_on.id != obj.id)
			{
				//Turn lop ON
				if(self.lop_on != null)
				{	 
					this.clearLop(self.lop_on);
				}
				
				self.lop_on = obj;
				var temp = "lop_data_" + obj.id.substring(4, (obj.id.length));
				document.getElementById(temp).className	= "lop_block_data_clicked";
				obj.className = "lop_block_on";				
			}
			else
			{			
				//Turn lop OFF
				self.lop_on = null;
				var temp = "lop_data_" + obj.id.substring(4, (obj.id.length));
				document.getElementById(temp).className	= "lop_block_data";	
				obj.className = "lop_block";							
			}	
		}
	}
	
	this.clearLop = function(obj, from)
	{
		var id_lop = obj.id.substring(4, obj.id.length);
		obj.className = "lop_block";
		document.getElementById("lop_data_" + id_lop).className = "lop_block_data";
	}	

	//--------------------------------------------
	//-------------JSON FUNCTIONALITY-------------
	//--------------------------------------------

	//To launch the search operation
	this.doSearch = function()
	{
		this.getParametersIn();
		this.getPoints();
	}
	
	this.whenPointsFetched = function()
	{
		var ret_val = null;
		self.points_list = this.preFormatPointsData();		
		this.addPoints();		
	}
	
	this.preFormatPointsData = function()
	{
		var ret_val = new Object();
		
		if(self.query_string.error != "no_results" && self.points_list.length > 0)
		{
			var points 				= [];
			var popup_template 		= "";
			var lop_template 		= "";
			var point_info 			= null;
		
			var lon_min	= null;
			var lon_max = null;
			var lat_min	= null;
			var lat_max = null;		
			
			var prevent_multiple_list = new Array();
		
			for(var point_id in self.points_list)
			{
				if(!prevent_multiple_list[self.points_list[point_id].info.point_id])
				{
					prevent_multiple_list[self.points_list[point_id].info.point_id] = true;
				
					point_info 				= self.points_list[point_id];
					point_info 				= self.points_list[point_id];
					point_info 				= self.points_list[point_id];				
					point_info["popup_pre"]	= this.formatPointPopup(point_info);	
			
					//Count bounds for the point area
					if(point_id == 0)
					{
						lon_min	= point_info["info"]["lon"];
						lon_max = point_info["info"]["lon"];
						lat_min	= point_info["info"]["lat"];
						lat_max = point_info["info"]["lat"];						
					}
			
					if(point_info["info"]["lon"] > lon_max) { lon_max = point_info["info"]["lon"]; }
					if(point_info["info"]["lon"] < lon_min) { lon_min = point_info["info"]["lon"]; }
					if(point_info["info"]["lat"] > lat_max) { lat_max = point_info["info"]["lat"]; }
					if(point_info["info"]["lat"] < lat_min) { lat_min = point_info["info"]["lat"]; }
			
					points.push(point_info);					
				}
			}


			ret_val.list 			= points;
			var bounds 				= new OpenLayers.Bounds(lon_min,lat_min,lon_max,lat_max);
			ret_val.bounds 			= bounds; 
			ret_val.is_empty 		= false;
		}
		else
		{		
			ret_val.list 			= new Array();
			var bounds 				= new OpenLayers.Bounds(0,0,0,0);
			ret_val.bounds 			= bounds; 
			ret_val.is_empty 		= true;			
		}
		
		return ret_val;
	}
	
	this.formatPointPopup = function(point_info)
	{
			var formatted = "";
			
			//Create popup layout
			var info = point_info["info"];
			
			var popup_template = self.popup_template.replace(/<!--replace_point_id-->/g, 	info["point_id"]);
			popup_template = popup_template.replace(/<!--replace_point_name-->/g, 			info["point_name"]);			
			popup_template = popup_template.replace(/<!--replace_date_creation-->/g, 		info["date_creation"]);			
			popup_template = popup_template.replace(/<!--replace_href_point_page-->/g, 		info["href_point_page"]);	
			popup_template = popup_template.replace(/<!--replace_lon-->/g, 					info["lon"]);	
			popup_template = popup_template.replace(/<!--replace_lat-->/g, 					info["lat"]);							
			popup_template = popup_template.replace(/<!--replace_creator_user_name-->/g, 	info["creator_user_name"]);	
			popup_template = popup_template.replace(/<!--replace_creator_user_id-->/g, 		info["creator_user_id"]);	
			formatted = popup_template;	
			return formatted;			
	}	
	
	this.getPoints = function()
	{
		var search_temp = "";
		var tags_temp 	= "";
				
		if(self.query_string.error != "no_results")
		{
			search_temp = "search=" + self.query_string.search;
			if(self.query_string.search_tags) { tags_temp = "&" + self.search_tags_parameter; } else { tags_temp = ""; }
	
			var xmlHttp;
  			try
    		{
    			// Firefox, Opera 8.0+, Safari  		
    			xmlHttp=new XMLHttpRequest();
    		}
  			catch (e)
    		{
    			// Internet Explorer
    			try
      			{
      				xmlHttp=new ActiveXObject("Msxml2.XMLHTTP");
      			}
    			catch (e)
      			{
      				try
        			{
        				xmlHttp=new ActiveXObject("Microsoft.XMLHTTP");
        			}
      				catch (e)
        			{
        				alert("Your browser does not support AJAX!");
        				return false;
        			}
      			}
    		}
    		
    		xmlHttp.onreadystatechange=function()
      		{
      			if(xmlHttp.readyState==4)
        		{
        	    	self.points_list = json_parse(xmlHttp.responseText);
        	    	self.whenPointsFetched();
        		}
      		}
    		xmlHttp.open("GET", self.um_url + "?" + search_temp + tags_temp, true);
    		xmlHttp.send(null);

        }	
        else
        {
        	self.query_string.search 			= "";
        	self.query_string.search_tags 		= "";
        	self.points_list = [];
       		self.whenPointsFetched();        	
        }	
	}
	
	this.getParametersIn = function()
	{
		self.query_string = new Object();
		var query_string = Querystring();
		
		if(query_string)
		{
			if(query_string.search)
			{
				query_string.search_array = query_string.search.split(" ");
				self.query_string = query_string;
				self.query_string.error = "";
			}
			else
			{
				self.query_string.error = "no_results";				
			}
		}
		else
		{
			self.query_string.error = "no_results";	
		}
	}
}


//----------------------------------------------------------------------------------------------------------------

function Querystring(qs) 
{ 
	

	this.params = {};

	this.get=Querystring_get;

	

	if (qs == null);

		qs=location.search.substring(1,location.search.length);



	if (qs.length == 0) 

		return;





	qs = qs.replace(/\+/g, ' ');

	var args = qs.split('&');

	

	for (var i=0;i<args.length;i++) {

		var pair = args[i].split('=');

		var name = unescape(pair[0]);

		

		var value = (pair.length==2)

			? unescape(pair[1])

			: name;

		

		this.params[name] = value;

	}
	
	return this.params;

}



function Querystring_get(key, default_) {

	var value=this.params[key];

	return (value!=null) ? value : default_;

}


//----------------------------------------------------------------------------------------------------------------

// json parser
// from json.org with small modification by Wensheng Wang
// http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/440637

    var cur_str_chr;
    function json_parse(text) {
        var at = 0;
        var ch = ' ';

        function error(m) {
            throw {
                name: 'JSONError',
                message: m,
                at: at - 1,
                text: text
            };
        }

        function next() {
            ch = text.charAt(at);
            at += 1;
            return ch;
        }

        function white() {
            while (ch !== '' && ch <= ' ') {
                next();
            }
        }

        function str() {
            var i, s = '', t, u;

            if (ch == '\'' || ch == '"') { //change " to ' for python
                cur_str_chr = ch;
outer:          while (next()) {
                    if (ch == cur_str_chr) {
                        next();
                        return s;
                    } else if (ch == '\\') {
                        switch (next()) {
                        case 'b':
                            s += '\b';
                            break;
                        case 'f':
                            s += '\f';
                            break;
                        case 'n':
                            s += '\n';
                            break;
                        case 'r':
                            s += '\r';
                            break;
                        case 't':
                            s += '\t';
                            break;
                        case 'u':
                            u = 0;
                            for (i = 0; i < 4; i += 1) {
                                t = parseInt(next(), 16);
                                if (!isFinite(t)) {
                                    break outer;
                                }
                                u = u * 16 + t;
                            }
                            s += String.fromCharCode(u);
                            break;
                        default:
                            s += ch;
                        }
                    } else {
                        s += ch;
                    }
                }
            }
            error("Bad string");
        }

        function arr() {
            var a = [];

            if (ch == '[') {
                next();
                white();
                if (ch == ']') {
                    next();
                    return a;
                }
                while (ch) {
                    a.push(val());
                    white();
                    if (ch == ']') {
                        next();
                        return a;
                    } else if (ch != ',') {
                        break;
                    }
                    next();
                    white();
                }
            }
            error("Bad array");
        }

        function obj() {
            var k, o = {};

            if (ch == '{') {
                next();
                white();
                if (ch == '}') {
                    next();
                    return o;
                }
                while (ch) {
                    k = str();
                    white();
                    if (ch != ':') {
                        break;
                    }
                    next();
                    o[k] = val();
                    white();
                    if (ch == '}') {
                        next();
                        return o;
                    } else if (ch != ',') {
                        break;
                    }
                    next();
                    white();
                }
            }
            error("Bad object");
        }

        function num() {
            var n = '', v;
            if (ch == '-') {
                n = '-';
                next();
            }
            while (ch >= '0' && ch <= '9') {
                n += ch;
                next();
            }
            if (ch == '.') {
                n += '.';
                while (next() && ch >= '0' && ch <= '9') {
                    n += ch;
                }
            }
            if (ch == 'e' || ch == 'E') {
                n += 'e';
                next();
                if (ch == '-' || ch == '+') {
                    n += ch;
                    next();
                }
                while (ch >= '0' && ch <= '9') {
                    n += ch;
                    next();
                }
            }
            if (ch == 'L')next();//for python long
            v = +n;
            if (!isFinite(v)) {
                error("Bad number");
            } else {
                return v;
            }
        }

        function word() {
            switch (ch) {
                case 't':
                    if (next() == 'r' && next() == 'u' && next() == 'e') {
                        next();
                        return true;
                    }
                    break;
                case 'f':
                    if (next() == 'a' && next() == 'l' && next() == 's' &&
                            next() == 'e') {
                        next();
                        return false;
                    }
                    break;
                case 'n':
                    if (next() == 'u' && next() == 'l' && next() == 'l') {
                        next();
                        return null;
                    }
                    break;
            }
            error("Syntax error");
        }

        function val() {
            white();
            switch (ch) {
                case '{':
                    return obj();
                case '[':
                    return arr();
                case '\'':
                case '"':
                    return str();
                case '-':
                    return num();
                default:
                    return ch >= '0' && ch <= '9' ? num() : word();
            }
        }

        return val();
    }
    //end json parser

function loadurl(dest, func, progress) {
    progress('LOADING');
    xmlhttp = window.XMLHttpRequest?new XMLHttpRequest(): new ActiveXObject("Microsoft.XMLHTTP");
    progress('LOADING.');
    xmlhttp.onreadystatechange = func;
    progress('LOADING..');
    xmlhttp.open("GET", dest);
    xmlhttp.setRequestHeader("If-Modified-Since", "Sat, 1 Jan 2000 00:00:00 GMT");
    progress('LOADING...');
    xmlhttp.send(null);
    progress('LOADING....');
}

function put_content_parsed() {
 if ((xmlhttp.readyState == 4) && (xmlhttp.status == 200)) {
  var json_data = json_parse(xmlhttp.responseText);
  var c = document.getElementById("dynamic_content");
  c.innerHTML = json_data[0];
 }
}

function put_content() {
 if ((xmlhttp.readyState == 4) && (xmlhttp.status == 200)) {
  var c = document.getElementById("dynamic_content");
  c.innerHTML = xmlhttp.responseText;
 }
}

function del_content() {
 var c = document.getElementById("dynamic_content");
 c.innerHTML = '';
}

function progress(s){
 var c = document.getElementById("dynamic_content");
 c.innerHTML = s;
}
