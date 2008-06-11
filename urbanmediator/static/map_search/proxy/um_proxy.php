<?php
	//Proxy
	@$tags 		= $_GET["tags"];
	@$search 	= $_GET["search"];
	
	if(!empty($search))
	{
		if(!empty($tags)) { $tags_addition = "tags=true&"; } else { $tags_addition = "";  }
		$url 			= "http://um.uiah.fi/final/feed/json/search?" . $tags_addition . "search=" . $search;
		$result_as_json = strip_tags(file_get_contents($url));
		print_r($result_as_json);
	}

?>