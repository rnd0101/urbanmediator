Urban Mediator web-server
=========================

Urban Mediator (UM) web-server is a software project of Icing research
project WP5 by ARKI research group of Media Lab of Univeristy of Art
and Design Helsinki.

UM utilizes client-server architecture and is a web application with a
usual web interface and mobile one.

Software in the package is under new BSD-like license (see LICENSE.txt)
except for the modules mentioned under Dependencies (they were shipped
with the UM software to make installation of the software easier for the 
end user)


Authors
-------
- Andrea Botero Cabrera, ARKI (project management) (2007)
- Eirik Fatland, ARKI (HCI, web design)
- Joonas Juutilainen, ARKI (some graphic design icons)
- Mika Myller, ARKI (software design) (2007)
- Iina Oilinki, ARKI (project management) (2006)
- Tommi Raivio, ARKI (software design, etc)
- Joanna Saad-Sulonen, ARKI (concept and user interface design)
- Roman Susi, ARKI (software design, etc)
- Tuomo Tarkiainen, ARKI (map search)
- Mark van der Putten, ARKI (HCI, web design, 2008)
- Abhigyan Singh, ARKI (usability tests, 2008)

and others.

Acknowledgements
----------------

The developers acknowledge the support for Urban Mediator provided by
the European Commission through FP6 contract number FP6-IST-2004-4 26665
(ICING PROJECT).

Web.py has been choosen for the framework.
Coordinate conversion given to us by the City Council of Helsinki.
We are in gratitude to the developers of the programs UM depends upon.

Dependencies
------------

Included with the Urban Mediator source code:

feedparser.py (UM uses slightly modified version)
    http://feedparser.org/
    (Open Source license)

BeautifulSoup
    http://www.crummy.com/software/BeautifulSoup/
    PSF license (same license as the Python)

FCKEditor
    http://www.fckeditor.net/
    MPL license (actually, it can be also distributed under GPL and LGPL)

OpenLayers
    http://www.openlayers.org/
    BSD License

freefont.ttf
    http://www.tulrich.com/fonts/  (renamed Tuffy font)
    Public Domain

webform.py
    has been derived from form.py of web.py
    Public Domain

Captcha code inspired/based on
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/440588

Icons from ExtFile/ExtImage (meant as temporary, to be replaced soon!):
    http://www.zope.org/Members/MacGregor/ExtFile

simplejson (encoder)
    http://undefined.org/python/#simplejson
    MIT license

json parser from json.org with small modification by Wensheng Wang
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/440637
    License?

Prerequisites
-------------

- Python 2.4.4 or 2.5.x
- MySQL v 5.0.38 or later
- MySQLdb v 1.2.2 - Python extension module
- web.py (0.22) - pure Python module
- elementtree - pure Python module (present in Python 2.5 readily)
- PIL (1.1.5 or later) - Python extension module
- pyproj (1.8.4 or later) - cartographic transformations and geodetic computations

Installation
============

Install (or check if they are installed) prerequisites mentioned above
according to their instructions for your operating system.

Important: (for web install) get hold of MySQL root password or password of a user
capable of creating new databases and users. In the example below:
root and SeCrEt respectively.

Hint: To setup root password for first time, use mysqladmin command at shell prompt as follows:
$ mysqladmin -u root password SeCrEt
(you may need to specify the full path to the mysqladmin executable, like
/usr/local/mysql/bin/mysqladmin )

Installing from tar.gz or zip
.............................

Untar and or unzip the package to the place where it will be run from.
(UM doesn't have ready start/stop scripts.)

Choose the port number (say, 9080) and the domain the UM will run
(e.g. localhost).

Go to the um root directory (of just untarred archive)
and run:

    python webinstall.py 9080

Go to the browser:

    http://localhost:9080

Fill in the form and press "Setup DB". If everything will go smoothly,
MySQL database and user will be created and tables created in the
databse. If not, webinstall can't be made - manual install is required. (Please, check MySQL root password carefully
before doing webinstall).

Visit local/config.py and add your changes. Most likely,
these will be needed:

base_url="http://my.server.org:9080"
schema_base_url = base_url + "/static"

WMS server also needs to be specified: metacarta.com is
just to quickly show UM.

Look into config.py for more configuration parameters: 
local/config.py override config.py settings.

Note about manual installation.

Instead of running webinstall:

- create a MySQL database and user with privileges to that DB

- put the latest sql/*-base.sql and sql/*-patch.sql with numbers greater than those of base.sql.

- put connection into local/config.py as follows (example only):

  db_parameters = dict(dbn='mysql', db='um_db', user='um', pw='*secret*')

- other configuration parameters

Running: can be done (in screen, for example):

  python code.py 9080

UM instance variable data is stored in the ~/.urban_mediator
(files as well as cached feeds and map tiles), docs, local
and in the MySQL database. (I.e., to move UM instance,
one should copy them all to the new place.). Logs are writted 
to stderr/stdout..

Installing from the egg
.......................

When UrbanMediator will be available in the PyPI, it
should be as easy as

east_install urban_mediator

Before that, download the egg file (the name is something like
urbanmediator-2.0_6409-py2.5.egg)

To install UM in the user space, setup PYTHONPATH to the
directory of choice (for example, in shell configuration file
like this:

export PYTHONPATH=/my/um/directory;other posible pathes

easy_install --install-dir=/my/um/directory urbanmediator-2.0_6409-py2.5.egg

After that, 

create a directory

/my/um/directory/local

and put config.py, plugins.py and other possible files.

To start web installer:

/my/um/directory/install_urbanmediator_server 9080

To start the server:

/my/um/directory/start_urbanmediator_server 9080

There is no way to stop the server but killing it.
file called PID with the server's process id
can be found in the /my/um/directory

Known issues
============

UrbanMediator software is designed to be a tool-kit for creation of specific city-citizens and/or citizens-citizens interactions. The main value is not software itself but the services it provides. The software itself is, however, not void of certain problems, bugs and limitations. Those are listed below in know specific order. (Issues, marked with "--" were solved)
1. Some glitches are possible with OpenLayers map portrayal depending on the browser. For example, click point shift may occur in some relatively rare cases.
2. Starting and stopping software is not automated. At the moment, on some platforms process should be explicitly killed to be stopped, especially, if there are active users fetching pages
--3. Search engines do not index UM pages due to some meta tags.
--4. Restarting UM back-end makes users logout
--5. No paging of comments, points, list in 1.0 beta(solved in the new UI)
--6. No way to add tags after point has been created (solved in the new UI)
--7. Sign-up disrupts user contribution (thus, user should sign up with UM beforehand or use Visitor account)
8. Problems with uploading large files on some platforms (limit about 2Mb)
9. Web installer is not user-friendly
10. When switching language, form entries are lost
--11. No way to relocate a point once created
12. Out-of-extent locations are not properly handled
13. Comments HTML is not sanitized enough at the moment (this may be security problem for the users with vulnerable browsers is malicious JavaScript is included by another user)
--14. Deletions from the database are not journalled
--15. Delay in loading Front page (and maybe other pages) caused by MySQL query on Mac OS X 10.4 (works fine on Linux Ubuntu/Debian)
16. New point policy "registered" is not enforced enough - visitors can still add points


