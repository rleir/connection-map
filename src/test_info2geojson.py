

import pytest
import info2geojson
import filecmp
from shutil import copyfile

# init contents
test_initlocFileName = "testData/InitLoc.json"
# the test loc DB
test_locFileName = "testData/testLoc.json"

test_inputNames  = "testData/nameTest.xlsx"
test_inputLoans  = "testData/loanTest.xlsx"
test_loan_connsGeoJSON = "testData/loanTest.geojson"


def init_test_loc_file():
    '''the loc file should not change in many tests below'''
    copyfile(test_initlocFileName, test_locFileName)


def test_open_json():
    init_test_loc_file()

    # read the locations json and initialize data structures:
    #               clear the count to 0
    # but do not scan the spreadsheet
    l1 = info2geojson.LoanInfo(test_locFileName,
                               test_inputNames,
                               test_inputLoans,
                               test_loan_connsGeoJSON)

    assert l1.loc_data["Gloucester Ontario Canada"]["latitude"] == 45.4473421

    l1.loc_data["Gloucester Ontario Canada"]["latitude"] == 99
    l1.write_location_DB()
    # output locations DB should still be correct
    #     and should equal the test check file
    assert filecmp.cmp(test_locFileName,
                       test_initlocFileName, shallow=False)

    l1.locations_changed = True
    l1.write_location_DB()

    # output locations DB should be incorrect
    #     and should not equal the test check file
    assert not filecmp.cmp(test_locFileName,
                           test_initlocFileName, shallow=False)

    l1.loc_data["Gloucester Ontario Canada"]["latitude"] == 45.4473421
    l1.write_location_DB()

    # output locations DB should be correct
    #     and should equal the test check file
    assert filecmp.cmp(test_locFileName,
                       test_initlocFileName, shallow=False)
    return True


def test_a_one_row():
    init_test_loc_file()
    l1 = info2geojson.LoanInfo(test_locFileName,
                               test_inputNames,
                               test_inputLoans,
                               test_loan_connsGeoJSON)
    assert filecmp.cmp(test_loan_connsGeoJSON,
                       "testData/test_A_oneLocConnRef.geojson", shallow=False)
    return True
