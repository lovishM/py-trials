#!/usr/bin/env python

# System imports
import os, sys, re
import requests, traceback

# Local imports
import book

# Global URL
_BASEURL = "http://www.obooksbooks.com"

class BooksDownload :
    def __init__(self, workdir) :
        self.workdir = workdir

    def getRequest(self, url) :
        try :
            r = requests.get(url)
        except Exception:
            print(traceback.format_exc())
            return None
        return r
        
    def downloadBooks(self) :
        for i in range(1 , 49) :
            url = _BASEURL + "/books/list_10_" + str(i) + '.html'
            r = self.getRequest(url)
            if r == None :
                print "Error: could not download " + url
                break

            pat = re.compile('<a href="/.*\.html" target="_blank"')
            for line in r.text.split("\n") :
                m = pat.findall(line)

                if len(m) < 1 : continue

                for token in line.split('</li>') :
                    idx = token.find('"')
                    if idx == -1 :
                        continue
                    token = token[idx + 1:]
                    self.getBook(token[:token.find('"')])

    def getBook(self, bookUrl) :
        print "Downloading book with url [" + bookUrl + "]"
        url = _BASEURL + bookUrl
        b = book.book(url, self.workdir)
        idx = b.current()
        if b.downloaded() :
            print 'Already downloaded'
            return
        if idx == 0 :
            idx = idx + 1
            r = self.getRequest(url)
            b.write(r.text)
            if b.isCorrupted() :
                print 'Skipped'
                return
            self.progress(50, idx)
            
        while (idx <= b.pages()) :
            idx = idx + 1
            url = bookUrl
            url = _BASEURL + url[:-5] + '_' + str(idx) + '.html'
            r = self.getRequest(url)
            b.write(r.text)
            self.progress(b.pages(), idx)
        print

    def progress(self, total, now) :
        percent = (now * 50) / total
        done = percent*'|'
        left = (50 - percent)*' '
        sys.stdout.write('\rProgress:       [' + done + left + ']')
        sys.stdout.flush()

if __name__ == '__main__' :

    # Get basedir
    script = sys.argv[0] 
    cwd = os.getcwd()
    relPath = script[:script.rfind('/')]

    # Change path to working directory
    os.chdir(cwd)
    os.chdir(relPath)

    # Book download repo is ${workdir}/repo
    workdir = os.getcwd() + '/repo'
    if not os.access(workdir, os.F_OK) :
        os.makedirs(workdir)

    # Initialize with workdir
    try :
        b = BooksDownload(workdir)
        b.downloadBooks()
    except KeyboardInterrupt:
        print 'Process interrupted, exiting'
