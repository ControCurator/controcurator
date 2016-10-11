# Get achive.org links for a set of URL's
# Input: set of URL's
# Output: most recent archive.org document for each URL

import requests
import csv
import json

archived = [] # list of archived urls

# get archival link
def getArchive(url):
    if url in archived:
        print 'existing:',url
        return archived[url]
    else:
        # get archive url
        try:
            # send query to archive.org
            query = requests.get('http://archive.org/wayback/available?url='+url).text
            response = json.loads(query)
            # get timestamp and url to the archived page
            timestamp = response['archived_snapshots']['closest']['timestamp']
            archived_url = response['archived_snapshots']['closest']['url']

            row = [url,timestamp,archived_url]
            print 'new:',url
            writer.writerow(row)
            return archived_url
        except Exception,e:
            print 'failed:',url
            print str(e)
            return False


if __name__=='__main__':

    # get list of documents
    # TODO: get from database
    with open('../Data/archive-links.csv', 'r') as archive:
        reader = csv.DictReader(archive)
        archived = {row['url']:row['archive'] for row in reader}

    archive = open('../Data/archive-links.csv', 'a')
    writer = csv.writer(archive)


    # get list of documents
    f = open('../Data/CompleteDataset.csv', 'r')
    reader = csv.DictReader(f)

    for row in reader:
        # get the contents for this url
        archived_url = getArchive(row['url'])
    f.close()
    archive.close()