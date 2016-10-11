# Step 3: Get content of list of webpages
# Input: raw html documents
# Output: content of html page

from readability import Document
import lxml
import os

# TODO: remove and get from database
folder = '../Data/1-raw/'
rfolder = '../Data/2-cleaned/'

# get contents of a webpage
def getContents(fname):
    file = open(folder+fname, "r")
    html = file.read()
    file.close()
    text = Document(html)
    content = text.summary().encode('ascii', 'ignore').decode('ascii')
    archive_id = '/web/'+fname.split('-')[4]+'/'
    content = content.replace(archive_id,'')
        
    # cache file
    file = open(rfolder+fname, "wb")
    file.write(content)
    file.flush()
    file.close()
    return content

if __name__=='__main__':

    # TODO: get from database
    sites = os.listdir(folder)
    for site in sites:

        try:
            # get the contents for this url
            content = getContents(site)
            print 'saved:',site

        except Exception,e:
            print 'failed:',site, str(e)
            
            continue

            # use justext for further boilerplate removal
            paragraphs = justext.justext(content, justext.get_stoplist("English"))
