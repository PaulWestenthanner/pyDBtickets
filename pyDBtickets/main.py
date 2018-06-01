# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import commands as cmd
import getopt
import re
import sys

from TrainTicketFile import TrainTicketFile

db_regex = "[A-Z0-9]{6}\.pdf"


def find_potential_ticket_pdfs(folder_to_search, db_regex=db_regex):
    list_folder_to_search = cmd.getstatusoutput("ls " + folder_to_search)
    if list_folder_to_search[0] != 0:
        raise IOError("error in listing folder: ls", folder_to_search)
    pot_tickets = [re.match(db_regex, filename) for filename in list_folder_to_search[1].split("\n")]
    pot_tickets = [folder_to_search + "/" + pt.group() for pt in pot_tickets if pt]
    return pot_tickets


def usage():
    print "python main.py -f /path/to/directory/with/tickets -i /path/to/directory/with/invoices -c /path/to/file/with/costs.ods"


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'f:i:c:h', ['folder=', 'invoice=', 'costs=', 'help'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    # config variables
    folder_to_search = "/home/paul/Downloads"  # default value if not otherwise specified in command line option
    invoice_dir = "/home/paul/Documents/Steuer/Rechnungen"  # default value if not otherwise specified in command line option
    cost_sheet = "/home/paul/Documents/Steuer/bills_eur.ods"  # default value if not otherwise specified in command line option

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
        else:
            usage()
            sys.exit(2)

    # find potential tickets
    potential_tickets = find_potential_ticket_pdfs(folder_to_search, db_regex)
    tickets = [TrainTicketFile(pt) for pt in potential_tickets]
    tickets = [t for t in tickets if t.ticket_document]  # drop the non-tickets
    for t in tickets:
        # todo add proper logging
        print ("ticket", t.filename)
        print ("from", t.ticket_document.from_to[0], "to", t.ticket_document.from_to[1], "on",
               t.ticket_document.travel_date.strftime("%Y-%m-%d"))
        print ("total price:", t.ticket_document.gross_price, "vat:", t.ticket_document.vat)
        print ("update cost sheet at", cost_sheet)
        t.update_cost_sheet(cost_sheet)
        print ("move to invoice directory", invoice_dir)
        t.move_to_invoice_dir(invoice_dir)


if __name__ == '__main__':
    main()