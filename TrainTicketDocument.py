# -*- coding: utf-8 -*-

import datetime
from utils import check_if_ticket
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class TrainTicketDocument(object):
    def __init__(self, ticket_text):
        if not check_if_ticket(ticket_text):
            raise ValueError("The text is not a train ticket")
        self.ticket_text = ticket_text
        self.is_return = "Einfache Fahrt" not in ticket_text
        self.date_bought = self.find_date_bought()
        self.travel_date = self.find_travel_date()
        self.travel_date_return = self.find_travel_date_return() if self.is_return else None
        self.from_to = self.find_from_to()
        self.amt_regex = "\d{1,3},\d{2}€"  # assume there are no tickets > 1000 euros
        self.vat_rate_full = 0.19
        self.vat_rate_disc = 0.07  # discounted vat rate on tickets with less than 100km
        self.gross_price = self.find_gross_price()
        self.vat = self.find_vat()


    def _extract_date(self, pattern):
        date_str = re.search(pattern, self.ticket_text.replace("\n", " ")).group()[-10:]
        return datetime.datetime.strptime(date_str, "%d.%m.%Y")

    def find_date_bought(self):
        pattern = "Die\s+Buchung\s+Ihres\s+Online-Tickets\s+erfolgte\s+am\s+\d{2}\.\d{2}\.\d{4}"
        return self._extract_date(pattern)

    def find_travel_date(self):
        pattern = "Hinfahrt\s+am\s+\d{2}\.\d{2}\.\d{4}"
        return self._extract_date(pattern)

    def find_travel_date_return(self):
        pattern = "Rückfahrt\s+am\s+\d{2}\.\d{2}\.\d{4}"
        return self._extract_date(pattern)

    def find_from_to(self):
        pattern = "(Hinfahrt: )([A-ZÄÖÜa-zäöü.() ]+)(\+City)?(\n+)([A-ZÄÖÜa-zäöü.() ]+)(\+City)?(\n|, mit (ICE|IC|EC|IC/EC|RE|RB))"
        extracted_groups = [x for x in re.search(pattern, self.ticket_text).groups() if
                            x != "+City" and x is not None]  # drop city ticket in order to get same lenght
        return extracted_groups[1], extracted_groups[3]

    def find_gross_price(self):
        pattern = "\nPreis\n(" + self.amt_regex + ")*"
        # there is a price column stating the prices of all single positions and the total price in the end
        # Hence it suffices to take the last amount
        last_amt = re.search(pattern, self.ticket_text).group().split("\n")[-1]
        return float(re.search("[0-9,]+", last_amt).group().replace(",", "."))

    def find_vat(self):
        def get_vat(rate):
            pattern_rate = "\nMwSt \(?D\)? {r}%\n(".format(r=rate) + self.amt_regex + "\n)*"
            # there is a price column stating the prices of all single positions and the total price in the end
            # Hence it suffices to take the last amount
            amts = re.search(pattern_rate, self.ticket_text)
            if amts:
                last_amt = [x for x in amts.group().split("\n") if x != ""][-1]
                vat_at_rate = float(re.search("[0-9,]+", last_amt).group().replace(",", "."))
            else:
                vat_at_rate = 0
            return vat_at_rate

        vat_19 = get_vat(int(self.vat_rate_full * 100))
        vat_7 = get_vat(int(self.vat_rate_disc * 100))

        # do some sanity checks
        if vat_19 == 0:
            if abs(self.gross_price - self.gross_price / (
                1 + self.vat_rate_disc) - vat_7) > 0.05:
                # difference can be more than 1 ct because in multiple positions multiple rounding can occur
                raise ValueError("discounted VAT does not match, expected {ex}, actual {ac}".format(
                    ex=self.gross_price - self.gross_price / (1 + self.vat_rate_disc), ac=vat_7))

        if vat_7 == 0:
            if abs(self.gross_price - self.gross_price / (
                1 + self.vat_rate_full) - vat_19) > 0.05:
                # difference can be more than 1 ct because in multiple positions multiple rounding can occur
                raise ValueError("full VAT does not match, expected {ex}, actual {ac}".format(
                    ex=self.gross_price - self.gross_price / (1 + self.vat_rate_full), ac=vat_7))

        return vat_19 + vat_7

    def get_new_filename(self):
        """
        rename the file to bahn_FROM_TO_traveldateYYYYMMDD.pdf
        FROM and TO is abbreviated to only 3 letters
        """
        new_name = u"bahn_" + self.from_to[0][:3] + self.from_to[1][:3] + self.travel_date.strftime("%Y%m%d")
        return unicode(new_name)
