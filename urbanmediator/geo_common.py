# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    No coordinate conversion plugin.
"""

# no conversion needed
def encode(*x):
    return x

decode = encode

