# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
def check_if_ticket(text):
    """
    check if some keywords are contained
    """
    criteria = """Online-Ticket,BahnCard,www.bahn.de/agb,www.bahn.de/reiseplan,App DB Navigator""".lower().split(
        ",")
    if sum(c in text.lower() for c in criteria) > 3:
        return True
    return False