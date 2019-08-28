#!/usr/bin/env python3
"""
Handy utility to add latlong data to a xls for use in a d3js map.
  read input names xls data file
  find the address cols
  read the loans file


  find the zzz cols from the xls
  google to find any unknown latlongs

  write a file for
  write a file for

"""

__author__ = "Richard Leir"
__copyright__ = "Copyright 2019, Richard Leir"
__credits__ = ["Sean Tudor", "Mike Bostock"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Richard Leir"
__email__ = "rleir at leirtech ddot com"
__status__ = "Production"

from xlrd import open_workbook  # type: ignore
import os
import geopy    # pip install geopy
import geopy.geocoders
from geopy.geocoders import GoogleV3
import json
from geojsonfile import write_geojson_file

# input xlsx spreadsheets
default_inputNames = "names.xlsx"
default_inputLoans = "loans.xlsx"

# Input and Output locations file
default_locFileName = 'locations.json'

# Output loan-connections file
default_loansGeoJSON = 'loans.geojson'


class LoanInfo:

default_locFileName,
                 default_inputNames,
                 default_inputLoans,
                 default_loansGeoJSON)

    loc_data = {}  # type: Dict

    def __init__(self,
                 locFileName,
                 inputNames,
                 inputLoans,
                 loansGeoJSON):
        self.locFileName  = locFileName
        self.inputNames   = inputNames
        self.inputLoans   = inputLoans
        self.loansGeoJSON = loansGeoJSON

        # read existing locations, zero each count
        with open(self.locFileName) as json_file:
            self.loc_data = json.load(json_file)



    def scan_names_spreadsheet(self, xlsx_filename):
        # read xls, find avg sheet
        wb = open_workbook(xlsx_filename)
        s_found    = None
        addrCols   = None
        orgCols    = None
        for sheet in wb.sheets():
            shname = sheet.name
            if shname.endswith("Acq xlsx"):
                s_found = 1
                for row in range(sheet.nrows):
                    if row == 0:
                        addrCols = self.get_address_columns(sheet, row)
                    else:
                        addr = self.get_row_address(sheet, row, addrCols)
                        self.save_row_address(addr)
            

if __name__ == "__main__":
    # execute only if run as a script

    l1 = LoanInfo(default_locFileName,
                 default_inputNames,
                 default_inputLoans,
                 default_loansGeoJSON)

    l1.scan_names_spreadsheet(default_inputNames)
    l1.scan_loans_spreadsheet(default_inputLoans)
    l1.write_location_DB()
    
# end zzzzzzzzzzzzzzzzzzzzzz

for each name
  save in dict
  close xlsx

read in locations

for each loan
  get the I/O, date
  find a name
  get the address and date
  accumulate country state province
    (by date range)
    
for each connection
  save target country position
  save magnitude I/O
    (by summing date ranges)
    
write in new format

data row
  target latlon
  magnitude
  name for popup
