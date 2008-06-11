__doc__ = """

Requires a Series 60 v3 (3rd Edition) phone with a built in
 GPS, eg the Nokia N95.
Also needs S60 Python 1.4 (signed), LocationRequestor for Python
 <http://discussion.forum.nokia.com/forum/showpost.php?p=311182>
 (dev cert signed), and either this as a sis (and dev cert signed)
 or the S60 Python Shell (dev cert singed)
(It isn't possible to use the built in positioning module supplied
 with S60 python, as that has way too many bugs still)

When dev cert signing, you probably need to give all the
 possible permissions, as the S60 v3 code signing model is really
 rather crap :(

If you want to use symbian signed online, be sure to get versions of
 the sis files with the right UID ranges.
You can get the LocationRequestor sis file with the right UID
 from <http://gagravarr.org/code/locationrequestor_3rd_opensign.sis>

GPL

Nick Burch - v0.02 (04/05/2008)

Rewritten by Roman Suzi

"""

import e32
import math
import socket
import time
import os
import thread
import appuifw
import urllib
#import webbrowser

def webbrowser_open(url):
  url = '4 ' + url # 4 means Start/Continue the browser specifying a URL
  b = 'BrowserNG.exe' # or with the full path b='z:\\sys\\bin\\BrowserNG.exe'
  e32.start_exe(b, ' "%s"' % url, 1) # the space between 'and " seems to be important so don't miss it!

import audio

import sys
sys.path.append('C:/Python')
sys.path.append('E:/Python')

has_locationrequestor = None
try:
    import locationrequestor
    has_locationrequestor = True
except ImportError:
    has_locationrequestor = False
except SymbianError:
    has_locationrequestor = False
if not has_locationrequestor:
    print "\n"
    print "LocationRequestor module not found\n"
    print "Download it from http://usa.dpeddi.com/locationrequestor_3rd_unsigned.sis before using this program"
    # Try to exit without a stack trace - doesn't always work!
    sys.__excepthook__=None
    sys.excepthook=None
    sys.exit()


global location, going
location = {}

def process_lr_update(args):
    """Process a location update from LocationRequestor"""
    global location

    if len(args) > 2:
        if str(args[1]) != 'NaN':
            location['lat_dec'] = args[1]
        else:
            print ".",
            return

        if str(args[2]) != 'NaN':
            location['long_dec'] = args[2]

        location['alt'] = "%3.1f m" % (args[3])

        location['tsecs'] = long(args[12]/1000) # ms not sec
        timeparts = time.gmtime( location['tsecs'] )
        print "la: %2.8f" % location['lat_dec'],
        print "lo: %2.8f" % location['long_dec']
    else:
        print ".",

class LocReq:
    def __init__(self):
        self.lr = locationrequestor.LocationRequestor()
        self.id = None
        self.default_id = self.lr.GetDefaultModuleId()
        self.type = "Unknown"
    def __repr__(self):
        return self.type
    def identify_gps(self):
        # Try for the internal first
        count = self.lr.GetNumModules()
        for i in range(count):
            info = self.lr.GetModuleInfoByIndex(i)
            if ((info[3] == locationrequestor.EDeviceInternal) and ((info[2] & locationrequestor.ETechnologyNetwork) == 0)):
                try:
                    self.id = info[0]
                    self.type = "Internal"
                    self.lr.Open(self.id)
                    print "Picked Internal GPS with ID %s" % self.id
                    self.lr.Close
                    return
                except Exception, reason:
                    # This probably means that the GPS is disabled
                    print "Error querying GPS %d - %s" % (i,reason)

        # Look for external if there's no internal one
        for i in range(count):
            info = self.lr.GetModuleInfoByIndex(i)
            if ((info[3] == locationrequestor.EDeviceExternal) and ((info[2] & locationrequestor.ETechnologyNetwork) == 0)):
                self.id = info[0]
                self.type = "External"
                print "Picked External GPS with ID %s" % self.id
                return
        # Go with the default
        self.id = self.default_id
        print "Default GPS with ID %s" % self.id
    def connect(self):
        self.lr.SetUpdateOptions(1, 45, 0, 1)
        self.lr.Open(self.id)

        # Install the callback
        try:
            self.lr.InstallPositionCallback(process_lr_update)
            self.connected = True
            print u"Connected to the GPS Location Service"
            return True
        except Exception, reason:
            disp_notices = "Connect to GPS failed with %s, retrying" % reason
            self.connected = False
            return False
    def process(self):
        e32.ao_sleep(0.4)
        return 1
    def shutdown(self):
        self.lr.Close()



def ask_cfg():
    url = SERVER_URL
    username = ''
    password = ''
    try:
        SERVER_URL1 = appuifw.query(u"Server URL:", 'text', unicode(SERVER_URL))
        if SERVER_URL1 is not None:
            url = SERVER_URL1
        USERNAME = appuifw.query(u"Username:", 'text')
        if USERNAME is not None:
            username = USERNAME
        PASSWORD = appuifw.query(u"Password:", 'text')
        if PASSWORD is not None:
            password = PASSWORD
    except:
        pass
    res = {'url': url, 'username': username, 'password': password}
    cfg_file = open("C:\\icing_cfg.txt", "w")
    cfg_file.write(repr(res))
    cfg_file.close()
    return res    

def cfg():
    try:    
        cfg_file = open("C:\\icing_cfg.txt", "r")
        res = eval(cfg_file.read())
    except:
        res = ask_cfg()
    return res

def dbg_except():
    import traceback, sys
    return " ".join(traceback.format_exception(*sys.exc_info()))


def tolog(s):
    log_file = open("C:\\gps.log", "a")
    log_file.write(s+"\n")
    log_file.close()

def tolog1(s):
    log_file = open("C:\\gpserrors.log", "a")
    log_file.write(s+"\n")
    log_file.close()


def bt_dev(skt):
    try:    
        cfg_file = open("C:\\gpsbt.txt", "r")
        address, services = eval(cfg_file.read())
    except:
        address, services = socket.bt_discover()
        cfg_file = open("C:\\gpsbt.txt", "w")
        cfg_file.write(repr((address, services)))
        cfg_file.close()
    return address, services
    

def gps_coordinates():
    haveFix = 0
    latitude_in, longitude_in = 0, 0
    latitude, longitude = 0, 0

    sock = socket.socket(socket.AF_BT, socket.SOCK_STREAM)

    address, services = bt_dev(socket)
    # print address, services, type(address), type(services)
    
    target = (address, services.values()[0])
    sock.connect(target)

    counter = 0
    running = 1
    while running:
        buffer = ""
        ch = sock.recv(1)
        while (ch != '$'):
            ch = sock.recv(1)
        while 1:
            if (ch == '\r'):
                break
            buffer += ch
            ch = sock.recv(1)
        if (buffer[0:6] == "$GPGGA"):
            counter += 1
            try:
                tolog(buffer)
                (GPGGA, utcTime, lat, ns, lon, ew, posfix, sats, hdop, alt, altunits, sep, sepunits, age, sid) = buffer.split(",")
                #print utcTime, "--", lat, lon, alt, "-", posfix
                print ":",
                latitude_in = float(lat)
                longitude_in = float(lon)
                haveFix = int(posfix)
            except:
                haveFix = 0

            if haveFix:
                zoom = 2
                if ns == 'S':
                    latitude_in = -latitude_in
                if ew == 'W':
                    longitude_in = -longitude_in

                latitude_degrees = int(latitude_in/100)
                latitude_minutes = latitude_in - latitude_degrees*100

                longitude_degrees = int(longitude_in/100)
                longitude_minutes = longitude_in - longitude_degrees*100

                latitude = latitude_degrees + (latitude_minutes/60)
                longitude = longitude_degrees + (longitude_minutes/60)
                debug = buffer[1:]

                running = 0  #!!!!
            else:
                time.sleep(0.5)
            if counter > MAX_NUMBER_OF_TRIES:
                latitude = longitude = None
                debug = buffer[1:]
                break

    sock.close()
    return latitude, longitude, debug


def gps_coordinates2():
    global location
    if not location:
        return None, None, "nofix"
    else:
        return location["lat_dec"], location["long_dec"], ""


def quit(*args):
    global going
    going = 0


def use_location():
    lat, lon, debug = gps_coordinates2()
    username = USERNAME
    password = urllib.quote(PASSWORD)
    if lat is None:
        webopen(DEBUG_FMT % vars())
    else:
        webopen(LATLON_FMT % vars())


MAX_NUMBER_OF_TRIES = 2000
MAX_NUMBER_OF_TRIES_GPS_NOT_READY = 2000
SERVER_URL = "@mobile_base_url@"

cf = cfg()
SERVER_URL = cf.get("url")
DEBUG_FMT = SERVER_URL + "@debug_fmt@"
LATLON_FMT = SERVER_URL + "@latlon_fmt@"


USERNAME  = cf.get("username")
PASSWORD  = cf.get("password")

print "* ICING MOBILE CLIENT *\n" + SERVER_URL

gps = LocReq()
gps.identify_gps()
# Not yet connected
gps.connected = False

counter = 0
going = 1


def remove_cfg():
    os.remove("C:\\icing_cfg.txt")
    sys.exit(0)

appuifw.app.menu = [(u"Go to browser (no GPS)", use_location ),
                    (u"Reset config", remove_cfg)]
appuifw.app.exit_key_handler = quit
appuifw.app.title = u"Urban Mediator"
appuifw.app.screen = "normal"

print "Welcome to UM Mobile!"

lat = lon = None

while going > 0:
    # Connect to the GPS, if we're not already connected
    if not gps.connected:
        worked = gps.connect()
        if not worked:
            # Sleep for a tiny bit, then retry
            e32.ao_sleep(0.2)
            continue

    # If we are connected to the GPS, read a line from it
    if gps.connected:
        redraw = gps.process()
        old_lat = lat
        lat, lon, debug = gps_coordinates2()
        if lat is not None:
            appuifw.app.menu = [(u"Go to browser", use_location )]
            if old_lat is None:
                audio.say("GPS ready")
            e32.ao_sleep(1)
    else:
        # Sleep for a tiny bit before re-trying
        e32.ao_sleep(0.2)

else:
    # All done
    gps.shutdown()

print "All done"
