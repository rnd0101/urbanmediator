#!/bin/sh

svn info | grep Revision: | cut -f 2 -d ' ' > revision.txt

