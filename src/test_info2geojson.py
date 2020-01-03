

import pytest
import info2geojson
import filecmp
import json
from shutil import copyfile

# init contents
test_initlocFileName = "testData/InitLoc.json"
# the test loc DB
test_locFileName = "testData/testLoc.json"

test_inputNames = "testData/NameTest.xlsx"
test_inputLoans = "testData/LoansTest.xlsx"
test_tempdbg    = "testData/tempdbg.json"
test_conns_json = "testData/LoanConnsTest.json"


def init_test_loc_file():
    '''the loc file should not change in many tests below'''
    copyfile(test_initlocFileName, test_locFileName)


def ensure_newline(fname):
    '''ensure that a file is terminated with a newline '''
    f = open(fname)
    flist = f.readline()
    f.close()
    if not flist.endswith("\n"):
        flist += "\n"
        f = open(fname, "w")
        f.write(flist)
        f.close()


def test_open_json():
    init_test_loc_file()

    # read the locations json and initialize data structures:
    # but do not scan the spreadsheet
    l1 = info2geojson.LoanInfo(test_locFileName)

    assert (l1.loc_db.loc_data["Gloucester Ontario Canada"]["latitude"]
            == 45.4473421)

    l1.write_location_DB()

    # output locations DB should be correct
    #     and should equal the test check file
    assert filecmp.cmp(test_locFileName,
                       test_initlocFileName, shallow=False)
    return True


def test_few_names():
    init_test_loc_file()
    l1 = info2geojson.LoanInfo(test_locFileName)
    l1.scan_names_spreadsheet(test_inputNames)

    assert "addr" not in l1.name_data[0].keys()
    assert "inst" not in l1.name_data[0].keys()
    assert "addr" not in l1.name_data[1].keys()
    assert "inst" not in l1.name_data[1].keys()

    assert l1.name_data[2]["addr"] == 'Ottawa Ontario Canada'
    assert l1.name_data[2]["inst"] == 'Smith & Mineral Club'

    assert "addr" not in l1.name_data[3].keys()
    assert "inst" not in l1.name_data[3].keys()

    assert l1.name_data[8]["addr"] == 'Cornwall Ontario Canada'
    assert l1.name_data[8]["inst"] == "Yea's Donuts"

    return True


def test_few_loans():
    init_test_loc_file()
    l1 = info2geojson.LoanInfo(test_locFileName)
    l1.scan_names_spreadsheet(test_inputNames)
    l1.scan_loans_spreadsheet(test_inputLoans)

    assert l1.conn_data['Gloucester Ontario Canada1992']["year"] == 1992
    assert l1.conn_data['Cornwall Ontario Canada1992']["year"] == 1992
    assert l1.conn_data['Cornwall Ontario Canada1993']["year"] == 1993
    assert l1.conn_data['Cornwall Ontario Canada1992']["magnitude"] == 3
    assert l1.conn_data['Cornwall Ontario Canada1993']["magnitude"] == 1

    assert l1.conn_data['Gloucester Ontario Canada1992']["magnitude"] == 1
    assert l1.conn_data['Gloucester Ontario Canada1993']["magnitude"] == 2

    l1.make_conn_list(test_conns_json)
    assert l1.conn_data['Cornwall Ontario Canada1992']["magnitude"] == 3
    with open(test_tempdbg, 'w', encoding='utf8') as json_file:
        json.dump(l1.conn_data, json_file)
    assert filecmp.cmp(test_tempdbg,
                       "testData/tempdbgRef.json", shallow=False)

    ensure_newline(test_conns_json)
    assert filecmp.cmp(test_conns_json,
                       "testData/LoanConnsTestRef.json", shallow=False)
    return True


if __name__ == "__main__":
    # execute only if run as a script
    test_open_json()
    test_few_names()
    test_few_loans()
