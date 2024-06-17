# Import SonarrAPI Class
from pyarr import SonarrAPI

import sys
from pprint import pprint

# Set Host URL and API-Key
host_url = 'http://192.168.1.15:8989'

# You can find your API key in Settings > General.
api_key = '1111'

# Instantiate SonarrAPI Object
sonarr = SonarrAPI(host_url, api_key)
pprint(dir(sonarr.lookup_series()))
sys.exit(0)

# Get and print TV Shows
print(sonarr.get_series())