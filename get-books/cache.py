# ------------------------
# Defined dbm cache class
# ------------------------

import os, dbm

class cache :

    def __init__(self, workdir) :
        self.cacheFile = workdir + '/.download'
        self.readDB = None

    def __del__(self) :
        if self.readDB != None :
            self.readDB.close()

    def put(self, dic) :
        try :
            self.db = dbm.open(self.cacheFile, 'c')
        except dbm.error :
            self.readDB = None
        for (key,value) in dic.iteritems() :
            self.db[key] = value
        self.db.close()

    def get(self, name) :
        if self.readDB == None :
            try :
                self.readDB = dbm.open(self.cacheFile, 'r')
            except dbm.error :
                self.readDB = None
                return {}
        output = None
        try :
            output = self.readDB[name]
        except KeyError:
            pass
        return output

