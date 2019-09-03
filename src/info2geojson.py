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



read in locations

for each loan
  get the I/O, date
  find a name
  get the address and date
  accumulate country state province
    (by date range)

for each connection location
  save target country position
  save magnitude I/O
    (by summing date ranges)
  save inst names for a popup

write in new format

data row
  target latlon
  magnitude
  name for popup



"""

# names list gives shorter list of places
# names list indexed by seq

# places are mostly ends of a connection
# loans list is just for a count giving line width


__author__ = "Richard Leir"
__copyright__ = "Copyright 2019, Richard Leir"
__credits__ = ["Sean Tudor", "Mike Bostock"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Richard Leir"
__email__ = "rleir at leirtech ddot com"
__status__ = "Production"

from xlrd import open_workbook  # type: ignore
# import os
# import geopy    # pip install geopy
# import geopy.geocoders
from geopy.geocoders import GoogleV3
import json
# zzzz from geojsonfile import write_geojson_file

# input xlsx spreadsheets
default_inputNames = "names.xlsx"
default_inputLoans = "loans.xlsx"

# Input and Output locations file
default_locFileName = 'locations.json'

# Output loan-connections file
default_loan_connsGeoJSON = 'loans.geojson'


class LoanInfo:

    loc_data = {}  # type: Dict
    name_data = []  # type: List
    locations_changed = False

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
        # read xls
        # for each name row
        #   save in array
        #   close xlsx
        wb = open_workbook(xlsx_filename)
        col_ids   = None
        for sheet in wb.sheets():
            shname = sheet.name
            if shname.endswith("Name"):
                for row in range(sheet.nrows):
                    if row == 0:
                        col_ids = self.get_address_columns(sheet, row)
                    else:
                        self.save_row_data(sheet, row, col_ids)

        wb.release_resources()
        del wb
        print(self.name_data)

    def get_address_columns(self, sheet, row):
        ''' determine which spreadsheet columns contain address info '''
        seqKeyCol  = None
        instCol    = None
        cityCol    = None
        provCol    = None
        countryCol = None
        addrCols   = None
        col_ids    = {}

        for col in range(sheet.ncols):
            hdr = sheet.cell(row, col).value
            if "INST2" == hdr:
                instCol = col
                col_ids["instCol"] = instCol
            elif "CITY" == hdr:
                cityCol = col
            elif "PROV" == hdr:
                provCol = col
            elif "COUNTRY" == hdr:
                countryCol = col
            elif "NameSeq" == hdr:
                seqKeyCol = col
                col_ids["seqKeyCol"] = seqKeyCol

        addrCols = (cityCol,  provCol,  countryCol)
        col_ids["addrCols"] = addrCols
        return col_ids

    def save_row_data(self, sheet, row,  col_ids):
        ''' get address info from a spreadsheet row '''
        addrCols = col_ids["addrCols"]
        addr = ""
        for col in range(sheet.ncols):
            if col in addrCols:
                addr += sheet.cell(row, col).value
                addr += ' '
        addr = addr.rstrip()  # remove the last space
        addr = addr.lstrip()  # remove any leading spaces

        instCol = col_ids["instCol"]

        name_rec = {}
        name_rec["addr"] = addr
        name_rec["inst"] = sheet.cell(row, instCol).value

        seqKeyCol = col_ids["seqKeyCol"]
        seqKey = sheet.cell(row, seqKeyCol).value
        while seqKey < self.name_data.length():
            self.name_data.append()
        self.name_data.append(name_rec)
        return

    def scan_loans_spreadsheet(self, xlsx_filename):
        # read xls
        # for each name row
        #   save in array
        #   close xlsx
        wb = open_workbook(xlsx_filename)
        col_ids   = None
        for sheet in wb.sheets():
            shname = sheet.name
            if shname.endswith("LOAN1"):
                for row in range(sheet.nrows):
                    if row == 0:
                        col_ids = self.get_key_columns(sheet, row)
                    else:
                        self.save_zzz_data(sheet, row, col_ids)

        wb.release_resources()
        del wb

    def get_key_columns(self, sheet, row):
        pass

    def save_zzz_data(self, sheet, row, col_ids):
        pass

    def write_location_DB(self):
        if self.locations_changed:
            # update the location DB file
            filename = self.locFileName
            with open(filename, 'w', encoding='utf8') as json_file:
                json.dump(self.loc_data, json_file)


if __name__ == "__main__":
    # execute only if run as a script

    l1 = LoanInfo(default_locFileName,
                  default_inputNames,
                  default_inputLoans,
                  default_loan_connsGeoJSON)

    l1.scan_names_spreadsheet(default_inputNames)
    l1.scan_loans_spreadsheet(default_inputLoans)
    l1.write_location_DB()
