# -*- coding: utf-8 -*-
from __future__ import print_function
import commands as cmd
import getopt
import re

from PyDBtickets.TrainTicketDocument import TrainTicketDocument

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

DEFAULT_DB_REGEX = r"[A-Z0-9]{6}\.pdf"


def find_potential_ticket_pdfs(folder_to_search, db_regex=DEFAULT_DB_REGEX):
    """
    Find potential tickets via pre-selecting on the name of the PDF via a regex.
    DB uses a combination of capitals and numbers for their tickets.
    :param folder_to_search: string, path to the folder to search for tickets
    :param db_regex: regex for tickets
    :return: list of strings: absolute paths to tickets
    """
    list_folder_to_search = cmd.getstatusoutput("ls " + folder_to_search)
    if list_folder_to_search[0] != 0:
        raise IOError("error in listing folder: ls", folder_to_search)
    pot_tickets = [re.match(db_regex, filename) for filename in
                   list_folder_to_search[1].split("\n")]
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


def main():
    """
    Identify tickets
    Rename them
    Add information to the cost sheet
    :return:
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'f:i:c:r:h',
                                   ['folder=', 'invoice=', 'costs=', 'regex=', 'help'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    # config variables
    # set default value if not otherwise specified in command line option
    folder_to_search = "/home/paul/Downloads"
    invoice_dir = "/home/paul/Documents/Steuer/Rechnungen"
    cost_sheet = "/home/paul/Documents/Steuer/bills_eur.ods"
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
        else:
            usage()
            sys.exit(2)

    # find potential tickets
    potential_tickets = find_potential_ticket_pdfs(folder_to_search, db_regex=db_regex)
    # drop the non-tickets
    tickets = []
    for pot_tick in potential_tickets:
        try:
            tickets += [TrainTicketDocument(pot_tick)]
        except ValueError:
            print ("not a ticket " + pot_tick)

    for tick in tickets:
        # todo add proper logging
        print("ticket", tick.filename)
        print("from", tick.from_to[0], "to", tick.from_to[1], "on",
              tick.travel_date.strftime("%Y-%m-%d"))
        print("total price:", tick.gross_price, "vat:", tick.vat)
        print("update cost sheet at", cost_sheet)
        tick.update_cost_sheet(cost_sheet)
        print("move to invoice directory", invoice_dir)
        tick.move_to_invoice_dir(invoice_dir)


if __name__ == '__main__':
    main()
