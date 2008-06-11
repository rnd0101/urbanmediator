# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    CSV report module
"""

import StringIO
import csv
import util

REPORT_FIELDS = """id title added author lat lon repr_lat repr_lon url description comments_count uniqtags""".split()

def report(points):
    """ Create CSV report from the board points
    """
    # 1 run: forming the fields (because tags are variable)
    tags = set()
    tags2 = set()
    for p in points:
        p.tagsset = p.tags.set()
        tags2 |= p.tagsset & tags
        tags |= p.tagsset
        if p.comments:
            p.description = util.first_line(p.comments.list()[0].text.replace("\n", " ").replace("\t", " "),
                                            10000)
        else:
            p.description = ''
        p.title = p.title.replace("\n", " ").replace("\t", " ")
    tags = sorted(list(tags2))

    # 2 run
    csv_f = StringIO.StringIO()
    csv_w = csv.writer(csv_f, delimiter="\t")

    csv_w.writerow(REPORT_FIELDS + tags)

    for p in points:
        tagspart = [(i in p.tagsset and 1 or '') for i in tags]
        p.uniqtags = " ".join(p.tagsset - tags2)
        row = [p[i] for i in REPORT_FIELDS]

        csv_w.writerow(row + tagspart)

    return csv_f.getvalue()
