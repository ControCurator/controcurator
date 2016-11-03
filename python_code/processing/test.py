import nltk
import re
import time
 
exampleArray = ['The incredibly intimidating NLP scares people away who are sissies.']
 
contentArray =['Starbucks is not doing very well lately.',
               'Overall, while it may seem there is already a Starbucks on every corner, Starbucks still has a lot of room to grow.']
 
def processLanguage():
    try:
        for item in contentArray:
            tokenized = nltk.word_tokenize(item)
            tagged = nltk.pos_tag(tokenized)
            #print tagged
 
            namedEnt = nltk.ne_chunk(tagged)
            for s in namedEnt:
            	if type(s) is nltk.Tree:
					t = ' '.join(c[0] for c in s.leaves())
					print s.label(), t
            time.sleep(1)
 
    except Exception, e:
        print str(e)
 
processLanguage()