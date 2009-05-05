
# Module import-base plugin registry

#import geocoding.helsinki as geocoding
#import geocoding_common as geocoding
import geocoding_osm as geocoding

#import geo.helsinki as geo
import geo_common as geo

import urbanmediator.adminusers as adminusers

identity_services = {
 '@admin': adminusers,   # or something like that
}

scrapers = {
}

try:
    execfile("local/plugins.py")  # local config overrides
except:
    pass
