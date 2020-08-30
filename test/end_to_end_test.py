# -*- coding: utf-8 -*-
import unittest
from unittest import mock
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


class TestPyDB(unittest.TestCase):

    def test_e2e_ticket_handling(self):
        with unittest.mock.patch('getopt.getopt',
                                 return_value=([('--config', f'{base_path}/configs/test_config.yml')],[])):
            main.main()

            try:
                self.assertTrue(isdir(base_path + "/Data/invoices/ust_2018_06"))
                self.assertTrue(isdir(base_path + "/Data/invoices/ust_2019_05"))
                self.assertTrue(isdir(base_path + "/Data/invoices/ust_2020_02"))

                # check if correct tickets were found and renamed
                expected_tickets_201806 = [u'bahn_ErlMün20180705.pdf',
                                    u'bahn_MünErl20180702.pdf',
                                    u'bahn_MünErl20180710.pdf'
                                    ]

                self.assertEqual(len(expected_tickets_201806),
                                 len(os.listdir(base_path + "/Data/invoices/ust_2018_06")))
                self.assertEqual(len(set(expected_tickets_201806).intersection(
                    set([x for x in os.listdir(base_path + "/Data/invoices/ust_2018_06")]))), 3)

                # check if tickets were moved
                expected_non_tickets = [u"cv.pdf", u"unicodeexample.pdf"]
                self.assertEqual(len(set(expected_non_tickets).intersection(
                    set(os.listdir(base_path + "/Data/input_pdfs")))), 2)

                # check if sheet was updated
                expected_rows = [
                                 ['bahn', 'München_Erlangen20180710', '2018-06-17', 12.52, 2.38, 14.9, 0.19, '2018-06',  'R2Q9KC'],
                                 ['bahn', 'München_Erlangen20180702', '2018-06-17', 16.3, 3.1, 19.4, 0.19, '2018-06', 'AM9PUE'],
                                 ['bahn', 'Erlangen_München20180705', '2018-06-17', 18.82, 3.58, 22.4, 0.19, '2018-06','44WDDW'],
                                 ['bahn', 'Metzingen(Württ)_München20200203', '2020-02-03', 24.49, 1.71, 26.20, 0.07, '2020-02', '4QUCE7'],
                                 ['bahn', 'Erfurt_München20190608', '2019-05-22', 35.21, 6.69, 41.9, 0.19, '2019-05', 'SSGCFS']
                                 ]
                new_rows = pyexcel.get_sheet(file_name=base_path + "/Data/blank_cost_sheet.ods").get_array()[3:]
                # pyexcel.get_sheet.get_array can have float imprecisions, therefore we clean them here
                new_rows = [[s if not isinstance(s, float) else round(s, 2) for s in row] for row in new_rows]
                self.assertTrue(all([new_row in expected_rows for new_row in new_rows]))
                self.assertTrue(all([ex_row in new_rows for ex_row in expected_rows]))
            finally:
                cleanup_data_dir()

if __name__ == "__main__":
    unittest.main()
