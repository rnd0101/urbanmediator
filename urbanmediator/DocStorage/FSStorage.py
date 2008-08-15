"""
Storing files (and metadata) in a filesystem directory.
Access by keys.

Written by Roman Suzi and placed into Public Domain.

"""

import os, shutil, pickle, glob


class FSStorage:

    METADATA_DIR_NAME = '.metadata'
    SPARE_ROOT = "ROOT"

    def __init__(self, storage_uri, work_dir, wrap_absolute_pathes=True):
        self.storage_uri = storage_uri
        self.work_dir = work_dir
        self.wrap_absolute_pathes = wrap_absolute_pathes

    def _keyToPath(self, key):
        if key == "":
            key = "." + self.SPARE_ROOT
        path = os.path.abspath(os.path.join(self.work_dir, key))
        if not path.startswith(self.work_dir):
            if self.wrap_absolute_pathes:
                new_key = self.SPARE_ROOT + \
                    os.path.abspath(os.path.join(self.work_dir, key))
                return self._keyToPath(new_key)
            else:
                raise KeyError("Key outside storage")
        return path

    def isMetadata(self, key):
        return os.path.split(os.path.split(key)[0])[1] == self.METADATA_DIR_NAME

    def isContainer(self, key):
        return os.path.isdir(self._keyToPath(key))

    def metadata(self, key):
        # this doesn check path!
        if self.isMetadata(key):
            return None
        if key == "":
            key = "." + self.SPARE_ROOT
        path_parts = list(os.path.split(key))
        path_parts.insert(1, self.METADATA_DIR_NAME)
        return os.path.join(*path_parts)

    def _stripPrefix(self, key):
        if key.startswith(self.work_dir):
            return key[len(self.work_dir):].lstrip("/")
        else:
            return key   # !!!

    def _makeDirs(self, path):
        dirname = os.path.dirname(path)
        try:
           os.makedirs(dirname)
        except OSError:
           pass
        if os.access(dirname, os.F_OK):
           return
        raise KeyError("Bad key value (dir)")

    def _encodeAndWrite(self, value, output_file):
        if isinstance(value, unicode):
            output_file.write(value.encode("utf-8"))
        elif isinstance(value, str):
            output_file.write(value)
        else:
            pickle.dump(value, output_file, 1)  # binary

    def _read(self, value, input_file):
        return input_file.read()  # efficiency? decoding?

    def _initMetadata(self, key, default_data={}):
        metadata_key = self.metadata(key)

        # check if .metadata is file - not dir (for some reason)
        path_parts = list(os.path.split(key))
        path_parts.insert(1, self.METADATA_DIR_NAME)
        metadata_dir_key = os.path.join(*path_parts[:-1])

        if not self.isContainer(metadata_dir_key):
            self.delItem(metadata_dir_key)  # remove .metadata file - should be dir
        if metadata_key and not self.hasItem(metadata_key):
            self.setItem(metadata_key, default_data.copy())

    def _delMetadata(self, key):
        metadata_key = self.metadata(key)
        if metadata_key and self.hasItem(metadata_key):
            self.delItem(metadata_key)

    def setItem(self, key, value):
        self._initMetadata(key)
        if self.isContainer(key):
            raise KeyError("Read only key")
        path = self._keyToPath(key)
        self._makeDirs(path)
        f = None

        if hasattr(value, "read"):
            try:
                f = open(path, "wb")
                shutil.copyfileobj(value, f, 1024**2)
            finally:
                f and f.close()
        else:
            try:
                f = open(path, "wb")
                self._encodeAndWrite(value, f)
            finally:
                f and f.close()

    def getItem(self, key, mode=None):
        if not mode and self.isMetadata(key):
            mode = "pickle"
        mode = mode or "str"
        self._initMetadata(key)
        path = self._keyToPath(key)
        if os.path.isdir(path):
            raise KeyError("Read only key")
        if mode == "unicode":
            try: return unicode(open(path, "rb").read(), "utf-8")
            except: raise KeyError("Bad key")
        if mode == "str":
            try: return open(path, "rb").read()
            except: raise KeyError("Bad key")
        elif mode == "file":
            try: return open(path, "rb")
            except: raise KeyError("Bad key")
        elif mode == "pickle":
            try: return pickle.load(open(path, "rb"))
            except: raise KeyError("Bad key or pickle error")

    def updateItem(self, key, d):
        if not self.isMetadata(key):
            return  # !!!
        i = self.getItem(key)
        i.update(d)
        self.setItem(key, i)
        return i

    def hasItem(self, key):
        path = self._keyToPath(key)
        if os.access(path, os.F_OK):
            return True
        return False

    def delItem(self, key):
        if not key:
            return   # can't delete directory itself
        try: self._delMetadata(key)
        except: pass
        path = self._keyToPath(key)
        if os.path.isdir(path):
            try: shutil.rmtree(path)
            except: pass  # silently remove?
        else:
            try: os.remove(path)
            except: pass  # silently remove?

    def listItems(self, key):
        if key == "":
            key = "."
        path = self._keyToPath(key)
        return [self._stripPrefix(fn) 
                    for fn in glob.glob(path+"/*")]

if __name__ == "__main__":
  fss = FSStorage("file:///home/rnduser/tmp/fs", "/home/rnduser/tmp/fs") 
  if 0:
    for it in fss.listItems("104_0802"):
        print fss.getItem(fss.metadata(it)), it
        fss.updateItem(fss.metadata(it), {'d': 234})
  if 0:
    fss.setItem("dfdf2", "VALUE")
    fss.setItem("../../dfdf33333", "VALUE")
    fss.setItem("dfdf1", (1,2,3))
    print fss.hasItem("dfdf1")
    print fss.getItem("dfdf1", mode="pickle")
    print fss.delItem("dfdf1")
    print fss.hasItem("dfdf1")
    print fss.listItems("")
    #print fss.delItem("ROOT")
    for it in fss.listItems(""):
        if not fss.isContainer(it):
            print fss.getItem(fss.metadata(it)), it

  if 0:
    fss.setItem("", "VALUE")

