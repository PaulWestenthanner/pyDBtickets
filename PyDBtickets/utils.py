# -*- coding: utf-8 -*-

"""
This module contains functions that might be useful throughout the whole package.
At the moment there are the following functions:
- check if ticket
"""


def check_if_ticket(text):
    """
    check if some keywords are contained
    """
    criteria = "Online-Ticket,BahnCard,www.bahn.de/agb,www.bahn.de/reiseplan,App DB Navigator"\
        .lower().split(",")
    print("Fulfilled criteria: ", [(c, c in text.lower()) for c in criteria])
    if sum(c in text.lower() for c in criteria) > 3:
        return True
    return False


class NotATicketError(ValueError):
    pass
