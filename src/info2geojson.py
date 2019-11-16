#!/usr/bin/env python3
"""
Handy utility to get latlong data from an xlsx for use in a d3js map.
  read input names xls data file
  find the address cols
  accumulate country state province
  save inst names for a popup
  read in locations db
  google to find any unknown latlongs
  read the loans file
  find the key cols from the xls
  for each loan
    use seq to find name record
    increment the loan counter
  write in new format


Output
  address is a combination of city,state,country input columns
    this becomes the key for the location db
  the Google search returns a lat,lon and an address field which
    is slightly different from our address.
    we save it to the DB and use it in the map hover pop-up

  name_data has one record for each valid row in the names input
  "loans" is a count of loan rows for each name

  "magnitude" or "mag" is the count of "loans" rows
      for a (city,prov,country) address
  institute count is increased
      by the count of input loan rows with the institute name

TBD    (by date range)??

"""

__author__ = "Richard Leir"
__copyright__ = "Copyright 2019, Richard Leir"
__credits__ = ["Sean Tudor"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Richard Leir"
__email__ = "rleir at leirtech ddot com"
__status__ = "Production"

import xlrd
import math
from geolocdb import geolocdb
from geojsonfile import geojsonfile

# input xlsx spreadsheets
default_inputNames = "names.xlsx"
default_inputLoans = "loans.xlsx"

# Input and Output locations file
default_locFileName = 'locations.json'

# Output loan-connections file
default_loan_conns_gj = 'loan_conns_geojson.js'

OTTAWA_LON_LAT = (-75.697, 45.421)
DEBUG = False

class LoanInfo:

    # names_data list is indexed by seq, and it has gaps (missing entries)
    # it also has many duplicated rows
    name_data = []  # type: List

    def __init__(self,
                 locFileName):
        self.name_data = []  # type: List

        # location information, read from a file.
        # when a location is missing,
        #   we google to fill it in and then save to file.
        self.loc_db = geolocdb(filename=locFileName)

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
            if shname.startswith("Name"):
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
        name_rec["seq"] = seqKey

        if seqKey < len(self.name_data):
            print("Error seqkey " + str(seqKey))
            print("Error name length " + str(len(self.name_data)))
        while seqKey > len(self.name_data):
            self.name_data.append({})
        self.name_data.append(name_rec)
        return

    def scan_loans_spreadsheet(self, xlsx_filename):
        # read xls
        # for each loan row
        #   bump counter in name array
        #   close xlsx
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

        self.name_data[seq]["seq"] = seq
        # a seq key of 0 indicates there is no name record
        if seq == 0:
            return
        # check length
        # check for "loans"
        if seq > len(self.name_data) - 1:
            print("Error: seq in loans, max seq in names ",
                  str(seq), len(self.name_data))
        elif "loans" not in self.name_data[seq].keys():
            print("Error: loans key missing " + str(seq))

        else:
            self.name_data[seq]["loans"] += 1

    def make_conn_list(self, filename):
        """
        for each name
          write geojson record
        """
        conn_data = {}

        for name in self.name_data:
            # names are sparse, so check if this record contains info
            if "addr" not in name.keys():
                continue

            # names need not have any associated loans, so ignore
            if name["loans"] <= 0:
                if DEBUG:
                    print("no loans for name ", name)
                continue

            addr = name["addr"]
            # skip loans to Ottawa, they would not display well
            #  (or maybe they would?)
            if addr == "Ottawa Ontario Canada":
                continue

            coords = self.loc_db.get_address(addr)
            if coords is None:
                print("Missing coords: ", addr)
            else:
                if addr not in conn_data.keys():
                    coords["magnitude"] = 0
                    conn_data[addr] = self.adjustLon(coords)
                    conn_data[addr]["org names"] = {}

                conn_data[addr]["magnitude"] += name["loans"]

                orgName = name["inst"]
                if orgName == "":
                    orgName = "individual(s)"  # a person, not an institution

                if orgName not in conn_data[addr]["org names"]:
                    try:
                        conn_data[addr]["org names"][orgName] = 0
                    except (Exception,  TypeError) as err:
                        print("missing orgname entry: {0}".format(err))
                        print(addr)

                conn_data[addr]["org names"][orgName] += name["loans"]

        geojsonfile.write_geojson_file(conn_data,
                                       filename,
                                       and_properties=True)
        return conn_data  # returned for testing only

    def adjustLon(self, coords):
        """ The great circle line generator automatically corrects
        the Longitude to be (relative to Ottawa) -180 to 180.
        However the leaflet marker that we place at the destination end
        of the line knows nothing of this, so we need
        to correct the longitude to be in this range.
        """
        zlon = coords["longitude"]
        if zlon > OTTAWA_LON_LAT[0] + 180.0:
            coords["longitude"] = zlon - 360.0
        return coords

    def write_location_DB(self):
        self.loc_db.write_location_DB()


if __name__ == "__main__":
    # execute only if run as a script

    l1 = LoanInfo(default_locFileName)

    l1.scan_names_spreadsheet(default_inputNames)
    l1.scan_loans_spreadsheet(default_inputLoans)
    l1.make_conn_list(default_loan_conns_gj)
    l1.write_location_DB()
