# ------------------------
# Defined dbm cache class
# ------------------------

# System imports
import dbm


class Cache:
    def __init__(self, workdir):
        self.cacheFile = workdir + '/.download'
        self.readDB = dbm.open(self.cacheFile, 'c')

    def __del__(self):
        if self.readDB is None:
            self.readDB.close()

    def put(self, dic):
        for (key, value) in dic.iteritems():
            self.readDB[key] = value

    def get(self, name):
        if self.readDB is None:
            return {}
        output = None
        try:
            output = self.readDB[name]
        except KeyError:
            pass
        return output
