
def rmlogs():
    import os
    for fn in ["C:\\gps.log", "C:\\gpserrors.log", "C:\\gpsbt.txt"]:
      try:
        os.remove(fn)
      except:
        print "!", fn, "cant remove"

def direc():
    import os
    print "MDIR", os.listdir(MDIR)
    print "SDIR", os.listdir(SDIR)
