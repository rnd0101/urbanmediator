
# XXX check before release!
# Module import-base plugin registry

#import geocoding.helsinki as geocoding
import geocoding_common as geocoding

#import geo.helsinki as geo
import geo_common as geo


try:
    import soap_adapters.iisys2 as iisys2
except:
    pass

try:
    import soap_adapters.iisys as iisys

    import soap_adapters.ismart as ismart
except:
    pass

import urbanmediator.adminusers as adminusers
import urbanmediator.icingusers as icingusers

identity_services = {
# '@iisys': __import__("iisys.users"),   # or something like that   
 '@barcelona': icingusers,
 '@helsinki': icingusers,
 '@dublin': icingusers,
 '@admin': adminusers,   # or something like that   
}

scrapers = {
# for html-scraping:
    "http://www.hvv.fi": "www_helsinkivirtualvillage_fi",
# for queries:
    "www.hel.fi": "www_hel_fi",
}

try:
    execfile("local/plugins.py")  # local config overrides
except:
    pass
