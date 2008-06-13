# -*- coding: UTF-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Python setup for the Urban Mediator
"""


from setuptools import setup, find_packages

# force utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

if sys.version_info[:2] < (2, 5):
    install_also_requires = ['elementtree >= 1.2.6',]
else:
    install_also_requires = []

try:
    revision = "-" + open("revision.txt").read().strip()
except:
    revision = "-0000"

setup(
    name = "urbanmediator",
    version = "2.0.0" + revision,
    description = """Sharing urban information in location-aware way.""",
    long_description = """
    Urban Mediator (UM) web-server is a software project of Icing
    research project WP5 by ARKI research group of Media Lab of
    Univeristy of Art and Design Helsinki.
    """,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Environment :: Handhelds/PDA's",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Natural Language :: Catalan",
        "Natural Language :: Finnish",
        "Natural Language :: Russian",
        "Natural Language :: Spanish",
        "Natural Language :: Dutch",
        "Programming Language :: Python",
        "Programming Language :: SQL",
        "Programming Language :: JavaScript",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
    keywords = "urban location map point topic sharing issues",
    platforms = ["any"],
    author = "ARKI group, MLAB, TAIK, Helsinki",
    license = "Modified BSD license",
    url = "http://um.uiah.fi",
    packages = find_packages(),
    package_data = {'urbanmediator': [
                    'static/m/*.py',
                    'locales/*',
                    'templates/*/*.html',
                    'docs/*',
                    ]},
    include_package_data = True,
    zip_safe = False,
    install_requires = ['web.py >= 0.21',
                        'PIL >= 1.1.5',
                        'setuptools'] + install_also_requires,
    entry_points="""
        [console_scripts]
        start_urbanmediator_server=urbanmediator.run_server:run_server
        install_urbanmediator_server=urbanmediator.webinstall:main
        """,
    )
