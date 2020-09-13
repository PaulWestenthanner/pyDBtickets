# -*- coding: utf-8 -*-

import datetime
import os
import re
import shutil

import pyexcel
import textract
from PyDBtickets.utils import check_if_ticket, NotATicketError



class TrainTicketDocument(object):
    def __init__(self, filename):
        self.filename = filename
        self.ticket_text = self.extract_text()

        if not check_if_ticket(self.ticket_text):
            raise NotATicketError("The text is not a train ticket")
        self.is_return = "Einfache Fahrt" not in self.ticket_text
        self.date_bought = self.find_date_bought()
        self.travel_date = self.find_travel_date()
        self.travel_date_return = self.find_travel_date_return() if self.is_return else None
        self.from_to = self.find_from_to()
        self.amt_regex = r"\d{1,3},\d{2}€"  # assume there are no tickets > 1000 euros
        self.gross_price = self.find_gross_price()
        self.vat, self.payed_vat = self.find_vat()


    def extract_text(self):
        """
        wrapper for textract to extract text from pdf
        :return: string
        """
        return textract.process(self.filename, encoding='utf-8').decode("utf-8")

    def _extract_date(self, pattern):
        # pylint: disable=anomalous-backslash-in-string
        """
        extract date from an "augmented" date pattern, e.g.
        re.compile("Hinfahrt\s+am\s+\d{2}\.\d{2}\.\d{4}")
        :param pattern: string
        :return: datetime.datetime
        """
        date_str = re.search(pattern,
                             self.ticket_text.replace("\n", " ")).group()[-10:]
        return datetime.datetime.strptime(date_str, "%d.%m.%Y")

    def find_date_bought(self):
        """
        extract the buy-date of the ticket. This is dependent on the sentence
        'Die Buchung Ihres Online-Tickets erfolgte am DD.MM.YYYY'
        being text that is extracted from the ticket
        :return: datetime.datetime
        """
        pattern = r"Die\s+Buchung\s+Ihres\s+Online-Tickets\s+erfolgte\s+am\s+\d{2}\.\d{2}\.\d{4}"
        return self._extract_date(pattern)

    def find_travel_date(self):
        """
        extract the travel date of the ticket. This is dependent on the sentence
        'Hinfahrt am DD.MM.YYYY'
        being text that is extracted from the ticket
        :return: datetime.datetime
        """
        pattern = r"Hinfahrt\s+am\s+\d{2}\.\d{2}\.\d{4}"
        return self._extract_date(pattern)

    def find_travel_date_return(self):
        """
        extract the return date of the ticket. This is dependent on the sentence
        'Rückfahrt am DD.MM.YYYY'
        being text that is extracted from the ticket.
        This is only calculated if the ticket is a return ticket
        :return: datetime.datetime
        """
        pattern = r"Rückfahrt\s+am\s+\d{2}\.\d{2}\.\d{4}"
        return self._extract_date(pattern)

    def find_from_to(self):
        """
        Extract information of start and destination of the trip
        :return: Tuple of strings, first being start, second being destination
        """
        pattern = r"(Hinfahrt: )([A-ZÄÖÜa-zäöü.() ]+)(\+City)?(\n+)([A-ZÄÖÜa-zäöü.() ]+)" \
                  r"(\+City)?(\n|, mit (ICE|IC|EC|IC/EC|RE|RB))"
        # drop city ticket
        extracted_groups = [x for x in re.search(pattern,
                                                 self.ticket_text).groups()
                            if x != "+City" and x is not None]
        return extracted_groups[1], extracted_groups[3]

    def find_gross_price(self):
        """
        Find gross price including VAT of the ticket
        :return: float, gross price
        """
        pattern = r"\nBetrag\n(" + self.amt_regex + ")*"
        # There is a price column stating the prices of all single positions and the
        # total price in the end
        # Hence it suffices to take the last amount
        last_amt = re.search(pattern, self.ticket_text).group().split("\n")[-1]
        return float(re.search(r"[0-9,]+", last_amt).group().replace(",", "."))

    def find_vat(self):
        """
        Find total VAT charged for the ticket.
        Especially for expensing the ticket this is necessary info.
        For one ticket there might be charged full (19%) and discounted (7%) VAT.
        :return: float, vat
        """
        def get_vat():
            # todo: this might not work if we have different vats
            pattern = r'\nMwSt \(?D\)?:? (\d{1,2})%\n\d+,\d+€\n([\s\S]*)' + str(self.gross_price).replace('.', ',')
            vat_rate_str, vat_at_rate_str_list = re.search(pattern, self.ticket_text).groups()
            payed_vat_list = vat_at_rate_str_list.rstrip('€\n').split('€\n')
            # multiple position case
            if len(payed_vat_list) > 1:
                # assert that we have always 2n+1 elements in the list
                assert len(payed_vat_list) % 2 == 1
                payed_var_as_str = [el for idx, el in enumerate(payed_vat_list) if idx % 2 == 0]
                payed_var = sum([round(float(el.replace(',', '.')), 2) for el in payed_var_as_str])
            # single position case. This is comparably easy
            else:
                payed_var = round(float(vat_at_rate_str_list.rstrip('€\n').replace(',', '.')), 2)
            return int(vat_rate_str) * 0.01, payed_var

        vat_rate, vat_at_rate = get_vat()

        # do some sanity checks in case some formats change
        if abs(self.gross_price - self.gross_price / (1 + vat_rate) - vat_at_rate) > 0.05:
            # difference can be more than 1 ct because in multiple positions multiple
            # rounding can occur
            raise ValueError("discounted VAT does not match, expected {ex}, actual {ac}".format(
                ex=self.gross_price - self.gross_price / (1 + vat_rate), ac=vat_at_rate))
        return vat_rate, vat_at_rate

    def get_new_filename(self):
        """
        rename the file to bahn_FROM_TO_traveldateYYYYMMDD.pdf
        FROM and TO is abbreviated to only 3 letters
        """
        new_name = "bahn_" + self.from_to[0][:3] + self.from_to[1][:3] +\
                   self.travel_date.strftime("%Y%m%d") + ".pdf"
        return new_name

    def move_to_invoice_dir(self, invoice_dir):
        """
        Move the ticket to the invoice directory and rename it on the fly.
        This is done via os.rename and might not work under windows.
        :param invoice_dir:
        :return:
        """
        # create a folder for vat every month. If it doesn't exist yet create it
        if not os.path.isdir(invoice_dir):
            raise ValueError("Invoice directory '%s' does not exist." % invoice_dir)
        target_dir = f'{invoice_dir}/ust_{self.date_bought.strftime("%Y_%m")}'
        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)

        shutil.copy(self.filename, f"{target_dir}/{self.get_new_filename()}")

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
                      "_".join(self.from_to) +
                      self.travel_date.strftime("%Y%m%d"),
                      self.date_bought.strftime("%Y-%m-%d"),
                      self.gross_price - self.payed_vat,
                      self.payed_vat,
                      self.gross_price,
                      self.vat,
                      self.date_bought.strftime("%Y-%m"),
                      self.filename.rstrip('.pdf').split('/')[-1]
                     ]
        sheet = pyexcel.get_sheet(file_name=sheet_file_path)
        if update_row not in sheet.row:
            sheet.row += update_row
            sheet.save_as(sheet_file_path, dest_encoding="utf-8")
