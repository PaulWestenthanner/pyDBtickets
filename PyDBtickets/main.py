# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import getopt
import re
import sys
import yaml

from PyDBtickets.TrainTicketDocument import TrainTicketDocument
from PyDBtickets.utils import NotATicketError
DEFAULT_DB_REGEX = r"[A-Z0-9]{6}\.pdf"


def find_potential_ticket_pdfs(folder_to_search, db_regex=DEFAULT_DB_REGEX):
    """
    Find potential tickets via pre-selecting on the name of the PDF via a regex.
    DB uses a combination of capitals and numbers for their tickets.
    :param folder_to_search: string, path to the folder to search for tickets
    :param db_regex: regex for tickets
    :return: list of strings: absolute paths to tickets
    """
    list_folder_to_search = os.listdir(folder_to_search)
    pot_tickets = [re.match(db_regex, filename) for filename in list_folder_to_search]
    pot_tickets = [folder_to_search + "/" + pt.group() for pt in pot_tickets if pt]
    return pot_tickets


def usage():
    """
    Example usage to be printed if --help flag is specified
    :return:
    """
    print("python main.py -f /path/to/directory/with/tickets -i "
          "/path/to/directory/with/invoices -c /path/to/file/with/costs.ods")
    print("param -f --folder    Folder to search for train tickets")
    print("param -i --invoice   Directory to invoices/bills")
    print("param -c --costs     File path to cost sheet (in ods format)")
    print("param -r --regex     Regex for pdf files to consider as potential train tickets")


def run(folder_to_search, invoice_dir, cost_sheet, db_regex):
    """
    Run main script with parameters

    :param folder_to_search:
    :param invoice_dir:
    :param cost_sheet:
    :param db_regex:
    :return:
    """

    # find potential tickets
    potential_tickets = find_potential_ticket_pdfs(folder_to_search, db_regex=db_regex)
    # drop the non-tickets
    tickets = []
    print(potential_tickets, len(potential_tickets))
    for pot_tick in potential_tickets:
        try:
            tickets += [TrainTicketDocument(pot_tick)]
        except NotATicketError:
            print("not a ticket " + pot_tick)

    for tick in tickets:
        # todo add proper logging
        print("ticket", tick.filename)
        print("from", tick.from_to[0], "to", tick.from_to[1], "on",
              tick.travel_date.strftime("%Y-%m-%d"))
        print("total price:", tick.gross_price, "payed_vat:", tick.payed_vat)
        print("update cost sheet at", cost_sheet)
        tick.update_cost_sheet(cost_sheet)
        print("move to invoice directory", invoice_dir)
        tick.move_to_invoice_dir(invoice_dir)


def main():
    """
    Identify tickets
    Rename them
    Add information to the cost sheet
    :return:
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'f:i:c:r:h:o',
                                   ['folder=', 'invoice=', 'costs=', 'regex=', 'config=','help'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    # config variables
    # set default value if not otherwise specified in command line option
    db_regex = DEFAULT_DB_REGEX

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif opt in ('-f', '--folder'):
            folder_to_search = arg
        elif opt in ('-i', '--invoice'):
            invoice_dir = arg
        elif opt in ('-c', '--costs'):
            cost_sheet = arg
        elif opt in ('-r', '--regex'):
            db_regex = arg
        elif opt in ('-o', '--config'):
            for var in ['folder_to_search', 'invoice_dir', 'cost_sheet']:
                assert var not in vars() or var not in globals()
            with open(arg, 'r+') as f:
                config = yaml.load(f)
            folder_to_search = config['folder_to_search']
            invoice_dir = config['invoice_dir']
            cost_sheet = config['cost_sheet_path']
        else:
            usage()
            sys.exit(2)
    run(folder_to_search, invoice_dir, cost_sheet, db_regex)


if __name__ == '__main__':
    main()
