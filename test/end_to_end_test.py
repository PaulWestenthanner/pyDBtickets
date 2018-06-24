# -*- coding: utf-8 -*-
import os
from os.path import abspath, dirname, isdir
from shutil import copytree, rmtree
from PyDBtickets import main
import pyexcel


base_path = dirname(dirname(abspath(__file__)))

# create backup of Data directory in order to restore inputs
if isdir(base_path + "/Data_backup"):
    rmtree(base_path + "/Data_backup")
copytree(base_path + "/Data", base_path + "/Data_backup")


def cleanup_data_dir():
    """
    clean data directory after testing

    delete data directory and copy backup to data directory
    :return:
    """
    rmtree(base_path + "/Data")
    copytree(base_path + "/Data_backup", base_path + "/Data")


folder_to_search = base_path + "/Data/input_pdfs"
cost_sheet_path = base_path + "/Data/blank_cost_sheet.ods"
invoice_dir = base_path + "/Data/invoices"
main.run(folder_to_search=folder_to_search,
         cost_sheet=cost_sheet_path,
         invoice_dir=invoice_dir,
         db_regex=main.DEFAULT_DB_REGEX
         )

try:
    assert isdir(base_path + "/Data/invoices/ust_2018_06")

    # check if correct tickets were found and renamed
    expected_tickets = [u'bahn_ErlMün20180705.pdf',
                        u'bahn_MünErl20180702.pdf',
                        u'bahn_MünErl20180710.pdf'
                        ]

    assert len(expected_tickets) == len(os.listdir(base_path + "/Data/invoices/ust_2018_06"))
    assert len(set(expected_tickets).intersection(
        set([x.decode("utf-8") for x in os.listdir(base_path + "/Data/invoices/ust_2018_06")]))
    ) == 3

    # check if tickets were moved
    expected_non_tickets = [u"cv.pdf", u"unicodeexample.pdf"]
    assert len(expected_non_tickets) == len(os.listdir(base_path + "/Data/input_pdfs"))
    assert len(set(expected_non_tickets).intersection(set(os.listdir(base_path + "/Data/input_pdfs")))) == 2

    # check if sheet was updated
    expected_rows = [[u'bahn', u'München_Erlangen20180710', u'2018-06-17', 12.52, 2.38, 14.9, u'2018-06'],
                     [u'bahn', u'München_Erlangen20180702', u'2018-06-17', 16.3, 3.1, 19.4, u'2018-06'],
                     [u'bahn', u'Erlangen_München20180705', u'2018-06-17', 18.82, 3.58, 22.4, u'2018-06']
                     ]
    new_rows = pyexcel.get_sheet(file_name=base_path + "/Data/blank_cost_sheet.ods").get_array()[-3:]
    assert all([new_row in expected_rows for new_row in new_rows])
    assert all([ex_row in new_rows for ex_row in expected_rows])
finally:
    cleanup_data_dir()
