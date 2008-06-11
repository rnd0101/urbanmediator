# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Dummy geocoding.
"""

def street_latlon(address, srs=None, metadata=None):
    raise ValueError

supported_srs = ()

# this is to have city-specific examples
def example():
    return None

def test():
    return street_latlon(example())

if __name__ == "__main__":
    print test()

