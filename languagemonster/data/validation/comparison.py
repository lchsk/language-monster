# -*- encoding: utf-8 -*-

def compare(session, target, out):
    """
        takes a list of OutItem objects and compares values to those
        in the database
    """

    for item in out:
        resp = session.query(target['data']).filter(
            target['data'].word_lower == item.b.lower()
        )

        for r in resp:
            print r.word, r.definition, r.language
