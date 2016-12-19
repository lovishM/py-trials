#!/usr/bin/env python

# System imports
import os
import re
import sys

# External imports
import requests
import traceback

# Local imports
import book

# Global URL
_BASEURL = "http://www.obooksbooks.com"


class BooksDownload :
    def __init__(self, workDir):
        self.workDir = workDir

    def getRequest(self, url):
        try:
            r = requests.get(url)
        except Exception:
            print(traceback.format_exc())
            return None
        return r
        
    def downloadBooks(self):
        for i in range(1, 49):
            url = _BASEURL + "/books/list_10_" + str(i) + '.html'
            r = self.getRequest(url)
            if r is None:
                print "Error: could not download " + url
                break

            pat = re.compile('<a href="/.*\.html" target="_blank"')
            for line in r.text.split("\n") :
                m = pat.findall(line)

                if len(m) < 1: continue

                for token in line.split('</li>'):
                    idx = token.find('"')
                    if idx == -1 :
                        continue
                    token = token[idx + 1:]
                    self.getBook(token[:token.find('"')])

    def getBook(self, bookUrl):
        url = _BASEURL + bookUrl
        b = book.Book(url, self.workDir)
        idx = b.current()
        if b.downloaded():
            return
        print
        if idx == 0:
            idx += 1
            r = self.getRequest(url)
            b.write(r.text)
            if b.isCorrupted():
                sys.stdout.write('\r' + url + ' :  url not found')
                sys.stdout.flush()
                return
            self.progress(b.heading(), 50, idx)
            
        while idx <= b.pages():
            nextIdx = idx + 1
            url = bookUrl
            url = _BASEURL + url[:-5] + '_' + str(nextIdx) + '.html'
            r = self.getRequest(url)
            b.write(r.text)
            self.progress(b.heading(), b.pages(), idx)
            idx = nextIdx

    def progress(self, title, total, now):
        percent = (now * 40) / total
        done = percent*'|'
        left = (40 - percent)*' '
        if len(title) > 40 :
            title = title[:36] + '... '
        sys.stdout.write('\r%-40s: [%s%s]' % (title, done, left))
        sys.stdout.flush()

if __name__ == '__main__':
    print "Books Downloader"

    # Get basedir
    script = sys.argv[0] 
    cwd = os.getcwd()
    relPath = script[:script.rfind('/')]

    # Change path to working directory
    os.chdir(cwd)
    os.chdir(relPath)

    # Book download repo is ${workDir}/repo
    workDir = os.getcwd() + '/repo'
    if not os.access(workDir, os.F_OK) :
        os.makedirs(workDir)

    # Initialize with workDir
    try :
        b = BooksDownload(workDir)
        b.downloadBooks()
    except KeyboardInterrupt:
        print 'Process interrupted, exiting'
