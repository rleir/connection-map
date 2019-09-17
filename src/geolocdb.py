"""
Handy utility to get latlong data from google and cache it in a local file DB.
"""
import os
from geopy import geocoders, exc      # pip install geopy
import json


class geolocdb:

    def __init__(self, filename):
        # Input and Output locations file
        self.locFileName = filename

        self.g = None
        self.gcount = 0
        self.locations_changed = False
        self.loc_data = {}  # type: Dict

        # read cached locations
        with open(self.locFileName) as json_file:
            self.loc_data = json.load(json_file)

    '''check if address was cached'''
    def get_address(self, address):
        coords = None
        if address in self.loc_data.keys():
            coords = self.loc_data[address]
        else:
            # get google info
            # limit the number of google lookups per run
            if self.gcount >= 10:
                return coords
            self.gcount = self.gcount+1

            if self.g is None:
                API_KEY = os.getenv("GOOGLEAPI")
                self.g = geocoders.GoogleV3(api_key=API_KEY)

            try:
                print(address)
                locatn = self.g.geocode(query=address,
                                        exactly_one=True,
                                        timeout=10)
                # some things you can get from the result
                # print(locatn.raw)

                geo_loc = {}
                geo_loc["latitude"]  = locatn.latitude
                geo_loc["longitude"] = locatn.longitude
                geo_loc["address"]   = locatn.address

                self.locations_changed = True
                self.loc_data[address] = geo_loc
                coords = geo_loc
            except (Exception, exc.GeocoderQueryError) as err:
                print("geopy error: {0}".format(err))
                print('... Failed to get a location for {0}'.format(address))

        return coords

    '''save to cache'''
    # def save_to_cache(self, address, location):

    def write_location_DB(self):
        if self.locations_changed:
            # update the location DB file
            filename = self.locFileName
            with open(filename, 'w', encoding='utf8') as json_file:
                json.dump(self.loc_data, json_file)


if __name__ == '__main__':
    pass
