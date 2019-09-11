#!/usr/bin/env python3
"""
Handy utility to get latlong data from an xlsx for use in a d3js map.
  read input names xls data file
  find the address cols
  accumulate country state province
  read in locations db
  google to find any unknown latlongs
  read the loans file
  find the key cols from the xls
for each loan
find the corresponding address


  get the I/O, date
  find a name
  get the address and date

    (by date range)

for each connection location
  save target country position
  save magnitude I/O
    (by summing date ranges)
  save inst names for a popup

for each loan
  use seq to find name record
    increment the loan counter

for each name
  if there are loans
    add to conn list
    if address exists
      bump name cont
    else
      add new conn with name count of 1

write in new format

data row
  target latlon
  magnitude
  name for popup
"""

# names list gives shorter list of places


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

import xlrd
# import os
import math
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
default_loan_conns = 'loan_conns.csv'


class LoanInfo:

    # location information, read from a file.
    # when a locatn is missing, we google to fill it in and then save to file.
    loc_data = {}  # type: Dict
    locations_changed = False

    # names_data list is indexed by seq, and it has gaps (missing entries)
    name_data = []  # type: List

    def __init__(self,
                 locFileName):
        self.name_data = []  # type: List

        self.locFileName  = locFileName

        # read existing locations, zero each count
        with open(self.locFileName) as json_file:
            self.loc_data = json.load(json_file)

    def scan_names_spreadsheet(self, xlsx_filename):
        # read xls
        # for each name row
        #   save in array
        #   close xlsx
        wb = xlrd.open_workbook(xlsx_filename)
        s_found = None
        col_ids = None
        for sheet in wb.sheets():
            shname = sheet.name
            if shname.endswith("Name"):
                s_found = 1
                for row in range(sheet.nrows):
                    if row == 0:
                        col_ids = self.get_address_columns(sheet, row)
                    else:
                        self.save_address_data(sheet, row, col_ids)

        if s_found is None:
            print("'Name' sheet not found in " + xlsx_filename)
        wb.release_resources()
        del wb

    def get_address_columns(self, sheet, row):
        ''' determine which spreadsheet columns contain address info '''
        cityCol    = None
        provCol    = None
        countryCol = None
        addrCols   = None
        col_ids    = {}

        for col in range(sheet.ncols):
            hdr = sheet.cell_value(row, col)
            if "INST2" == hdr:
                col_ids["instCol"] = col
            elif "CITY" == hdr:
                cityCol = col
            elif "PROV" == hdr:
                provCol = col
            elif "COUNTRY" == hdr:
                countryCol = col
            elif "NameSeq" == hdr:
                col_ids["seqKeyCol"] = col

        addrCols = (cityCol,  provCol,  countryCol)
        col_ids["addrCols"] = addrCols
        return col_ids

    def save_address_data(self, sheet, rowx,  col_ids):
        ''' get address info from a spreadsheet row '''
        addrCols = col_ids["addrCols"]
        addr = ""
        for col in range(sheet.ncols):
            if col in addrCols:
                addr += sheet.cell_value(rowx, col)
                addr += ' '
        addr = addr.rstrip()  # remove the last space
        addr = addr.lstrip()  # remove any leading spaces

        instCol = col_ids["instCol"]

        name_rec = {}
        name_rec["addr"] = addr
        name_rec["inst"] = sheet.cell_value(rowx, instCol)
        name_rec["loans"] = 0
        colx = col_ids["seqKeyCol"]

        cty = sheet.cell_type(rowx, colx)
        # XL_CELL_NUMBER indicates a float
        if not cty == xlrd.XL_CELL_NUMBER:
            print("Error: cell type " + str(cty))
        seqKey = math.floor(sheet.cell_value(rowx, colx))

        if seqKey < len(self.name_data):
            print("Error seqkey " + str(seqKey))
            print("Error name length " + str(len(self.name_data)))
        while seqKey > len(self.name_data):
            self.name_data.append({})

        self.name_data.append(name_rec)
        return

    def scan_loans_spreadsheet(self, xlsx_filename):
        wb = xlrd.open_workbook(xlsx_filename)
        s_found = None
        col_ids = None
        for sheet in wb.sheets():
            shname = sheet.name
            if shname.endswith("LOAN1"):
                s_found = 1
                for row in range(sheet.nrows):
                    if row == 0:
                        col_ids = self.get_key_columns(sheet, row)
                    else:
                        self.save_key_data(sheet, row, col_ids)
        if s_found is None:
            print("'LOAN' sheet not found in " + xlsx_filename)
        wb.release_resources()
        del wb

    def get_key_columns(self, sheet, rowx):
        col_ids = {}
        for colx in range(sheet.ncols):
            hdr = sheet.cell_value(rowx, colx)
            if "SeqFromName" == hdr:
                col_ids["seqFromCol"] = colx
            elif "DATE" == hdr:
                col_ids["date"] = colx
        return col_ids

    def save_key_data(self, sheet, rowx, col_ids):
        colx = col_ids["seqFromCol"]
        cval = sheet.cell_value(rowx, colx)
        if cval == "":
            return
        try:
            seq = math.floor(cval)
        except TypeError:
            print("Error: typeerr row col ", str(rowx), str(colx), str(cval))
            return
        # a seq key of 0 indicates there is no name record
        if seq == 0:
            return
        # check length
        # check for "loans"
        if seq > len(self.name_data) - 1:
            print("Error: name seq out of range  " + str(seq))
            print(self.name_data)
        elif "loans" not in self.name_data[seq].keys():
            print("Error: loans key missing " + str(seq))

        else:
            self.name_data[seq]["loans"] += 1

    def make_conn_list(self, filename):
        OTTAWA_LON_LAT = ("-75.697", "45.421")
        f = open(filename, 'w')
        f.write('long1,long2,lat1,lat2,loan_count\n')
        for name in self.name_data:
            if "addr" not in name.keys():
                continue
            loan_count = name["loans"]
            name_addr = name["addr"]
            # skip loans to Ottawa, they would not display well
            #  (or maybe they would?)
            if name_addr == "Ottawa Ontario Canada":
                continue
            if name_addr in self.loc_data.keys():
                coords = self.loc_data[name_addr]
                zlon = coords["longitude"]
                zlat = coords["latitude"]
                row =  OTTAWA_LON_LAT[0] + ','
                row += str(zlon) + ','
                row += OTTAWA_LON_LAT[1] + ','
                row += str(zlat) + ','
                row += str(loan_count) + '\n'
                f.write(row)
            else:
                print("location missing for " + name_addr)
        f.close()

    def write_location_DB(self):
        if self.locations_changed:
            # update the location DB file
            filename = self.locFileName
            with open(filename, 'w', encoding='utf8') as json_file:
                json.dump(self.loc_data, json_file)


if __name__ == "__main__":
    # execute only if run as a script

    l1 = LoanInfo(default_locFileName)

    l1.scan_names_spreadsheet(default_inputNames)
    l1.scan_loans_spreadsheet(default_inputLoans)
    l1.make_conn_list(default_loan_conns)
    l1.write_location_DB()
