# Download raw code of set of websites
# Input: (archive) links
# Output: html page

import requests
import csv
import os

# turn url into safe filename
def getFilename(url):
    filename = url.replace('/','-')
    keepcharacters = (' ','.','_','-')
    fname = "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()
    return fname

# download webpage from url
def getDocument(url):
    fname = getFilename(url)
    if os.path.isfile('../Data/1-raw/'+fname+'.html'):
        file = open('../Data/1-raw/'+fname+'.html', "r")
        html = file.read()
        file.close()
        print 'existing:',url
        return html
    else:
        # download html
        try:
            html = requests.get(url).text.encode('ascii', 'ignore').decode('ascii')
            print 'new:',url
        except Exception,e:
            print 'failed:',url
            print str(e)
            return False
        
        # cache file
        file = open('../Data/1-raw/'+fname+'.html', "wb")
        file.write(html)
        file.flush()
        file.close()
        return html

if __name__=='__main__':
    # get list of documents
    f = open('../Data/archive-links.csv', 'r')
    reader = csv.DictReader(f)

    for row in reader:
        # get the contents for this url
        html = getDocument(row['archive'])
    f.close()