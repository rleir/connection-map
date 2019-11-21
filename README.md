# connection-map

[![Build Status](https://travis-ci.com/rleir/connection-map.svg?branch=master)](https://travis-ci.com/rleir/connection-map)
[![DeepScan grade](https://deepscan.io/api/teams/5622/projects/7454/branches/75997/badge/grade.svg)](https://deepscan.io/dashboard#view=project&tid=5622&pid=7454&bid=75997)

## A Site and a data preparation utility

You will notice some similarities with the latlong-col project. Both projects get input information from xlsx spreadsheets and display interactive LeafletJS maps.

Both projects share the locations.json DB. You might want to use filesystem links and make sure you don't run both data utilities simultaneously.

### The web site: a connection map using LeafletJS

This zoomable Leaflet map shows great circle lines from Ottawa to institutions receiving loans from the museum.

The icons show the locations of institutions. Hover over a location to see a popup naming the partner organizations.

Files:

*  src/site_conn/index.html
*  src/site_conn/Leaflet.Geodesic.js
*  src/site_conn/loan_conns_geojson.js
*  src/site_conn/conn_map.js

### The data utility: get place and loan data from two xlsx files

The site above uses data files prepared by this utility. It gets name and place info from an xlsx, and does a join with data from a loans xlsx.

Files:

*  src/info2geojson.py
*  src/geojsonfile.py
*  src/geolocdb.py

Input:

*  names.xlsx
*  loans.xlsx

Outputs:

*  locations.json
*  loan_conns_geojson.js

The goal is to get the lat/long values for locations, for use in the map. We do a google search using the address info from the spreadsheet.

When Google is being consulted, we save a list of lat/lons in a file locations.json. We don't want to be calling Google every time this program is run, so we keep track of what has already been searched.

We occasionally experience timeouts from Google, so we have an algorithm which can be run multiple times, each time adding to locations.json.

During development we limit the number of google searches to 10 per run.

You need an API key from Google for use in searches. Store the key in the GOOGLEAPI environment variable before running addLatLong.py .  Before the first run, manually create a null locations.json file.

We should be able to add rows to the xlsx and do another run to get the additional locations.

Run it:

$ python3 info2geojson.py

Test it:

$ pytest

Steps:

*  read locations.json
*  read input xls data files,
*  determine which columns contain the address
*  read all rows, saving the address, counting repetitions of an address
*  for each address, google to find the latlongs
*  write the updated locations.json

Bugs

*  The geojson file produced by the utility needs a manual edit to prefix it with "connData =" and suffix it with ";".
