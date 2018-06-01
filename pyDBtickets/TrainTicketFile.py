# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import commands as cmd
import os
import pyexcel
import textract

from TrainTicketDocument import TrainTicketDocument
from utils import check_if_ticket

class TrainTicketFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.ticket_text = self.extract_text()
        self.ticket_document = TrainTicketDocument(self.ticket_text) if check_if_ticket(self.ticket_text) else None


    def extract_text(self):
        return textract.process(self.filename, encoding='utf_8')

    def move_to_invoice_dir(self, invoice_dir):
        # create a folder for vat every month. If it doesn't exist yet create it
        if not os.path.isdir(invoice_dir):
            raise ValueError("Invoice directory '%s' does not exist." % invoice_dir)
        target_dir = invoice_dir + "/ust_" + self.ticket_document.date_bought.strftime("%Y_%m")
        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)

        move_statement = "mv {f} {target}/{newname}".format(f=self.filename,
                                                                target=target_dir,
                                                                newname=self.ticket_document.get_new_filename())

        status = cmd.getstatusoutput(move_statement)[0]
        if status != 0:
            raise ValueError("Error while moving: " + move_statement)

    def update_cost_sheet(self, sheet_file_path):
        """
        format of cost sheet is
        u'Spent at',
        u'Purpose',
        u'Rechnungsdatum',
        u'Amount Net',
        u'VAT',
        u'Gross',
        u'Ust In / Buchungsmonat'
        """
        update_row = ["bahn",
                      unicode("_".join(self.ticket_document.from_to) + self.ticket_document.travel_date.strftime("%Y%m%d")),
                      self.ticket_document.date_bought.strftime("%Y-%m-%d"),
                      self.ticket_document.gross_price - self.ticket_document.vat,
                      self.ticket_document.vat,
                      self.ticket_document.gross_price,
                      self.ticket_document.date_bought.strftime("%Y-%m")
                      ]
        sheet = pyexcel.get_sheet(file_name=sheet_file_path)
        sheet.row += update_row
        sheet.save_as(sheet_file_path, dest_encoding="UTF-8")
