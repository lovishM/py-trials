# -------------------------
# Definition of book class
# -------------------------

# System imports
import cPickle as cPK

# Local imports
import cache


class Book:
    def __init__(self, url, workDir):
        self.h = None
        self.p = 0
        self.c = 0
        self.d = False
        self.corrupted = False

        self.url = url
        self.dir = workDir
        self.cache = cache.Cache(self.dir)

        self.fp = None

        self.load()
        if self.h:
            self.fp = open(self.dir + "/" + self.h + ".txt", 'a+')

    def load(self):
        pickle = self.cache.get(self.url)
        if pickle:
            data = cPK.loads(pickle)
            self.h = data["heading"]
            self.p = data["pages"]
            self.c = data["current"]
            self.d = data["downloaded"]

    def sync(self):
        data = {
            "heading": self.h,
            "pages": self.p,
            "current": self.c,
            "downloaded": self.d
        }
        self.cache.put({self.url: cPK.dumps(data)})

    def __del__(self):
        if self.fp:
            self.fp.close()

    def downloaded(self):
        return self.d

    def write(self, content):
        content = self.parse(content)
        if self.h is None:
            self.corrupted = True
            self.sync()
            return
        if not self.fp:
            self.fp = open(self.dir + '/' + self.h + '.txt', 'a+')

        self.fp.write(content.encode("utf-8"))
        self.c += 1
        if self.c == self.p:
            self.d = True
        self.sync()

    def pages(self):
        if self.p:
            return self.p
        return 1

    def heading(self):
        if self.h:
            return self.h
        return ''

    def current(self):
        return self.c

    def isCorrupted(self):
        return self.corrupted

    def parse(self, data):

        body = False
        content = ''
        for token in data.split('\n'):
            if not self.h and '<h1>' in token:
                self.h = token.strip()
                self.h = self.h.replace('<h1>', '')
                self.h = self.h.replace('</h1>', '')
                self.h = self.h.replace('/', ' or ')
                continue
            if body:
                if '<table' in token:
                    body = False
                else:
                    if not content:
                        content = ' '
                        continue
                    temp = token
                    temp = temp.replace('<div>', '')
                    temp = temp.replace('</div>', '')
                    if temp.strip():
                        temp = temp.replace('&nbsp;', '')
                        temp = temp.replace('<p>', '').replace('</p>', '')
                        temp = temp.replace('&quot;', '"').replace("&#39;", "'")
                        temp = temp.replace('&ldquo;', '"').replace('&rdquo;', '"')
                        temp = temp.replace("&lsquo;", "'").replace("&rsquo;", "'")
                        content += temp + '\n'
                continue

            if not body and '<div class="text"' in token:
                body = True
                continue
            if (self.p == 0) and not body and '<li><a>Total' in token:
                temp = token.strip()
                temp = temp[temp.find('<a>') + 3:]
                temp = temp[:temp.find('<')]
                temp = temp.replace('Total ', '')
                temp = temp[:temp.find(' ')]
                self.p = int(temp)
                break
        return content
