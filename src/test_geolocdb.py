

import pytest
from unittest import mock
import geolocdb
import filecmp
from shutil import copyfile

# init contents
test_initlocFileName = "testData/InitLoc.json"
# the test loc DB
test_locFileName = "testData/testLoc.json"


def init_test_loc_file():
    '''the loc file should not change in many tests below'''
    copyfile(test_initlocFileName, test_locFileName)


def test_open_json():
    init_test_loc_file()

    # read the locations json and initialize data structures:

    # but do not scan the spreadsheet
    g1 = geolocdb.geolocdb(test_locFileName)

    assert g1.loc_data["Gloucester Ontario Canada"]["latitude"] == 45.4473421

    g1.loc_data["Gloucester Ontario Canada"]["latitude"] = 99
    g1.write_location_DB()
    # output locations DB should still be correct
    #     and should equal the test check file
    assert filecmp.cmp(test_locFileName,
                       test_initlocFileName, shallow=False)

    g1.locations_changed = True
    g1.write_location_DB()

    # output locations DB should be incorrect
    #     and should not equal the test check file
    assert not filecmp.cmp(test_locFileName,
                           test_initlocFileName, shallow=False)
    g1.loc_data["Gloucester Ontario Canada"]["latitude"] = 45.4473421
    g1.write_location_DB()

    # output locations DB should be correct
    #     and should equal the test check file
    assert filecmp.cmp(test_locFileName,
                       test_initlocFileName, shallow=False)
    return True


# def fake_geocoders.GoogleV3():
#    return True
#
# test that an access to a known address does not cause a google call,
# and the DB is not changed
def test_get_known():
    init_test_loc_file()

    # read the locations json and initialize data structures:

    # but do not scan the spreadsheet
    g1 = geolocdb.geolocdb(test_locFileName)
    coords = g1.get_address("Gloucester Ontario Canada")
    assert coords["latitude"] == 45.4473421
    assert coords["longitude"] == -75.5942867
    assert coords["address"] == "Gloucester, Ottawa, ON, Canada"

    g1.write_location_DB()

    # output locations DB should be correct
    #     and should equal the test check file
    assert filecmp.cmp(test_locFileName,
                       test_initlocFileName, shallow=False)
    return True


# test that an access to an unknown address causes a google call,
# and the result gets saved
def test_get_new():
    init_test_loc_file()

    # read the locations json and initialize data structures:

    # but do not scan the spreadsheet
    g1 = geolocdb.geolocdb(test_locFileName)
    g1.get_address("Kingston Ontario Canada")
    return True
