#!/usr/bin/env python3
"""
Handy utility to reformat the locations file for use in a d3js map.
  read input locations data file
  for each location, generate a feature record
  write the features data file
    (two versions of this file, with and without the Institution Names)
"""

__author__ = "Richard Leir"
__copyright__ = "Copyright 2019, Richard Leir"
__credits__ = ["Sean Tudor", "Mike Bostock"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Richard Leir"
__email__ = "rleir at leirtech ddot com"
__status__ = "Production"

from typing import Dict, List
import json


class geojsonfile:

    def write_geojson_file(all_data, filename, and_properties) -> None:
        ''' generate feature rec with lat lon position for each address '''

        fea_data = {}  # type: Dict
        fea_data["type"] = "FeatureCollection"
        metadata = {}  # some dummy metadata
        metadata["generated"] = 1559586926000   # dummy
        metadata["url"] = "https://zzzz/"       # dummy
        metadata["title"] = "zzz"               # dummy
        metadata["status"] = 200                # dummy
        metadata["api"] = "1.8.1"               # dummy
        metadata["count"] = len(all_data)
        fea_data["metadata"] = metadata

        features = []
        fea_data["features"] = features

        for addr in all_data:
            feature = {}
            props = {}
            geometry = {}

            # if "address" not in addr:  # check for key existence
            if "address" not in all_data[addr]:  # check for key existence
                print("key existence check ", addr)
                continue    # skip this record
            if "magnitude" not in all_data[addr]:  # check for key existence
                print("mag existence check ", addr)
                continue    # skip this record
            if all_data[addr]["magnitude"] <= 0:  # check for unused location
                print("mag zero check ", addr)
                continue    # skip this record

            props["place"] = all_data[addr]["address"]
            props["year"] = all_data[addr]["year"]
            props["mag"] = float(all_data[addr]["magnitude"])
            props["nameseq"] = all_data[addr]["nameseq"]
            coordinates = []
            coordinates.append(all_data[addr]["longitude"])
            coordinates.append(all_data[addr]["latitude"])
            coordinates.append(9)
            geometry["type"] = "Point"
            geometry["coordinates"] = coordinates
            feature["type"] = "Feature"
            feature["properties"] = props
            feature["geometry"] = geometry
            feature["id"] = "zzz"
            features.append(feature)

            if not and_properties:
                continue
            if "org names" not in all_data[addr]:
                continue
            props["popupContent"] = {}
            for org in all_data[addr]["org names"]:
                if org == 0:
                    print("org zero check ", addr)
                    continue    # skip this record
                props["popupContent"][org] = all_data[addr]["org names"][org]

        with open(filename, 'w', encoding='utf8') as json_file:
            json.dump(fea_data, json_file)


if __name__ == '__main__':
    pass
