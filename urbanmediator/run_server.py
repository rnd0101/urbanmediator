#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Main file to run the Urban Mediator server.
"""

import os, sys

current_dir = os.getcwd()

import urbanmediator

import urbanmediator.config as config


def run_server():
    fh = open("PID", "w")
    fh.write(str(os.getpid()))
    fh.close()

    if getattr(config, "listen_ip_port", ""):
        try:
            sys.argv[1] = config.listen_ip_port
        except:
            sys.argv.insert(1, config.listen_ip_port)

    config.package_dir = os.path.dirname(urbanmediator.__file__)
    config.static_dir = os.path.join(config.package_dir, "static")
    os.chdir(config.package_dir)  #!!!
    urbanmediator.code.main()


if __name__ == "__main__":
    run_server()
