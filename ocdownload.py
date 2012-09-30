
#!/usr/bin/env python3

# downloads every ocremix

from bs4 import BeautifulSoup
from urllib import request, parse, error
from os import path, makedirs
import re
from multiprocessing.pool import ThreadPool

DIR = "songs" # this is where stuff gets downloaded to
MAX_CONNECTIONS = 1 # parallel stuff works really well but ocremix.org blocks us then :/

# figure out newest song and then just work backwards towards 00001
site_newest = request.urlopen("http://ocremix.org/remixes/?&offset=0&sort=datedesc").read()
soup_newest = BeautifulSoup(site_newest)
link_newest = soup_newest.find(href=re.compile("OCR0[0-9]*")).get('href')
newest_number = int(re.search('[0-9]+', link_newest).group(0))
print("Highest number is " + str(newest_number))

pool = ThreadPool(MAX_CONNECTIONS) # this many concurrent connections

def download_song(number):
    # not all songs will be found, some will be 404
    try:
        padded_number = str(number).zfill(5)
        url_song = "http://ocremix.org/remix/OCR" + padded_number + "/"
        print("Trying " + url_song)
        site_song = request.urlopen(url_song).read()

        soup_song = BeautifulSoup(site_song)
        link_song = soup_song.find(text="Download from ocrmirror.org").parent.get('href')
        filename = path.basename(parse.urlparse(link_song)[2])

        print("Downloading " + filename)
        data = request.urlopen(link_song)
        if not path.exists(DIR):
            makedirs(DIR)
        output = open(DIR + "/" + filename, 'wb')
        output.write(data.read())
        output.close()
    except error.HTTPError:
        print("Didn't find OCR " + padded_number)

output = pool.map(download_song, range(1, newest_number + 1))
