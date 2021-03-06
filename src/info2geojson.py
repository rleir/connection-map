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
import copy

# input xlsx spreadsheets
default_inputNames = "names.xlsx"
default_inputIOLoans = "loans.xlsx"     # Outgoing loans

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
    conn_data = {}

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
        datemode = wb.datemode

        s_found = None
        col_ids = None
        for sheet in wb.sheets():
            shname = sheet.name
            if shname.endswith("LOAN1"):
                s_found = 1
                for row in range(sheet.nrows):
                    if row == 0:
                        col_ids = self.get_loans_columns(sheet, row)
                    else:
                        self.save_loans_data(sheet, row, col_ids, datemode)
        if s_found is None:
            print("'LOAN' sheet not found in " + xlsx_filename)
        wb.release_resources()
        del wb

    def get_loans_columns(self, sheet, rowx):
        col_ids = {}
        for colx in range(sheet.ncols):
            hdr = sheet.cell_value(rowx, colx)
            if "SeqFromName" == hdr:
                col_ids["seqFromCol"] = colx
            elif "IO" == hdr:
                col_ids["input-output"] = colx

            elif "DATE" == hdr:
                col_ids["date"] = colx
            elif "Date" == hdr:
                col_ids["date"] = colx

            elif "Date recorded" == hdr:
                col_ids["dateRec"] = colx
            elif "DATEDUE" == hdr:
                col_ids["dateDue"] = colx
            elif "DATERETURN" == hdr:
                col_ids["dateRet"] = colx
        return col_ids

    def get_date_data(self, sheet, rowx, colx, datemode):
        year = ""
        cval = sheet.cell_value(rowx, colx)
        if cval != "":
            try:
                year = xlrd.xldate_as_tuple(cval, datemode)[0]
            except xlrd.xldate.XLDateNegative:
                print("Warn: row col year ", str(rowx), str(colx),
                      str(cval), year)
        # this is strange, but we end up with the correct year value
        if rowx == 3930:
            print("row 3930 should be=2005 year ", year, " cval ", cval)
        if rowx == 3778:
            print("row 3778 should be=2004 year ", year, " cval ", cval)
        return year

    def save_loans_data(self, sheet, rowx, col_ids, datemode):
        # get the year from the date or date recorded or date returned column
        year = 0
        colx = col_ids["date"]
        year = self.get_date_data(sheet, rowx, colx, datemode)

        if year == 0:
            colx = col_ids["dateDue"]
            year = self.get_date_data(sheet, rowx, colx, datemode)
        if year == 0:
            colx = col_ids["dateRet"]
            year = self.get_date_data(sheet, rowx, colx, datemode)
        if year == 0:
            colx = col_ids["dateRec"]
            year = self.get_date_data(sheet, rowx, colx, datemode)
        if year == 0:
            print("no date====== ", rowx)

        colx = col_ids["input-output"]
        i_o = sheet.cell_value(rowx, colx)

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
        if seq > len(self.name_data) - 1:
            print("Error: seq in loans, max seq in names ",
                  str(seq), len(self.name_data))
            return
        self.build_conn_list(seq, year, i_o)

    def build_conn_list(self, seq, year, i_o):
        # add a record to  the connection list

        if "addr" not in self.name_data[seq].keys():
            print("missing name rec, seq ", seq)
            return

        addr = self.name_data[seq]["addr"]
        # skip loans to Ottawa, they would not display well
        #  (or maybe they would?)
        if addr == "Ottawa Ontario Canada":
            return
        coords = self.loc_db.get_address(addr)
        if coords is None:
            print("Missing coords: ", addr)
            return

        conn_key = addr + str(year)

        if self.conn_data.get(conn_key) is None:
            newrec = self.adjustLon(coords)
            newrec["year"] = copy.copy(year)
            newrec["magnitude"] = 0
            newrec["org names"] = {}
            newrec["nameseq"] = []  # this is just for debugging
            self.conn_data[conn_key] = copy.copy(newrec)

        self.conn_data[conn_key]["nameseq"].append(seq)
        self.conn_data[conn_key]["magnitude"] += 1

        orgName = self.name_data[seq]["inst"]
        if orgName == "":
            orgName = "individual(s)"  # a person, not an institution

        orgNameIO = i_o + orgName
        if orgNameIO not in self.conn_data[conn_key]["org names"]:
            try:
                self.conn_data[conn_key]["org names"][orgNameIO] = 0
            except (Exception,  TypeError) as err:
                print("missing orgnameI entry: {0}".format(err))
                print(conn_key)
        self.conn_data[conn_key]["org names"][orgNameIO] += 1

    def make_conn_list(self, filename):
        """
        for each name
          write geojson record
        """
        geojsonfile.write_geojson_file(self.conn_data,
                                       filename,
                                       and_properties=True)

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
    l1.scan_loans_spreadsheet(default_inputIOLoans)
    l1.make_conn_list(default_loan_conns_gj)
    l1.write_location_DB()
