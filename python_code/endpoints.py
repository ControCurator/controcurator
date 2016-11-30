#!/bin/python
from __future__ import division
'''

This file provides an active learning environment for the demo interface.
Needs the file 'Topic.xlsx' as input.


Description of functionality
---

data model:
    COMMENT KASPAR: I interpreted 'score' as the class of the noun phrase, i.e. 0 or 1.
    datapoint = { str(noun phrase) : { 'score': float(controversy score), 'confidence':float(confidence)}}
    estimates = l st(datapoint1, .... , datapointN) 
    labelled  = { str(noun phrase) : { 'label' : 'controversial' OR 'noncontroversial') , 'ip' : str(ip address of user) } }

---

Controversy is labelled on the noun-phrase (here considered topic) level. 
Timestamps should be implemented on the backend side. 

'''
import random # while real data lacks
import json
import sys
import os
# KB: Added modules
import numpy as np
import pandas as pd
import random
# libact classes
from libact.base.dataset import Dataset
from libact.models import LogisticRegression
from libact.query_strategies import UncertaintySampling

from elasticsearch import Elasticsearch

from esengine import Payload, Query, Filter
from models.anchor import *


es = Elasticsearch(
    ['http://controcurator.org/ess/'],
    port=80)



def load_anchors():


    #query = es.search(index="anchors", doc_type="vaccination")#, query=body)
    #topTopics = top['aggregations']['topics']['buckets']

    anchors = Anchor.all(size=20)


    data = pd.DataFrame([a.type]+[a.features for a in anchors], index=[a._id for a in anchors])
    '''
    We need to keep track of the original topic name. This information is needed 
    when asking the user whether the topic is controversial
    '''
    
    names = data.index
    
    ''' 
    As features we currently only look at # of 'positive' words (col 3),
    # of 'negative' words (col 4), and'intensity' (col 5).
    '''
    
    X = np.asarray(data.ix[:,2:3])

    '''
    The active learning environment used here (libact) needs a few coded observation.
    Otherwise search new data points won't work
    Since the existing spreadsheet already ranked topics according to their controversy scores, 
    I made a best guess, and assigned the first five to class 1 (controversial) and the last five
    to class 0 (not controversial)
    '''
    
    y = np.asarray([1,1,1,1,1] + [None]*(X.shape[0]-10)+[0,0,0,0,0])
    return X,y,names


def load_data(path_to_file):
    '''
    Okay, let's load the Excel spreadsheet in which topics, 
    here understood as noun phrases, are given controversy scores.
    '''
    data = pd.read_excel(path_to_file, header=None,skiprows=1)

    
    '''
    We need to keep track of the original topic name. This information is needed 
    when asking the user whether the topic is controversial
    '''
    
    names = list(data.ix[:,0])
    
    ''' 
    As features we currently only look at # of 'positive' words (col 3),
    # of 'negative' words (col 4), and'intensity' (col 5).
    '''
    
    X = np.asarray(data.ix[:,3:5])

    '''
    The active learning environment used here (libact) needs a few coded observation.
    Otherwise search new data points won't work
    Since the existing spreadsheet already ranked topics according to their controversy scores, 
    I made a best guess, and assigned the first five to class 1 (controversial) and the last five
    to class 0 (not controversial)
    '''
    
    y = np.asarray([1,1,1,1,1] + [None]*(X.shape[0]-10)+[0,0,0,0,0])

    return X,y,names


def initialize_model(X,y):
    '''
    Convert feature matrix and target vector to a format that is 
    easy to digest for the libact model and searchers
    '''
    trn_ds = Dataset(X,y)

    '''
    Define model. We start with a simple Logistic Regression.
    More refined models can be implemented later.
    There is a possibility to integrate Sklearn classifiers.
    '''
    model=LogisticRegression()

    '''
    Before looking for new datapoins the model needs to fitted using
    the scarce observation we have given, see the construction of the 'y'
    target vector in the load_data function
    '''
    model.train(trn_ds)
    return model,trn_ds

def convert_label(label):
    '''
    Function that converts manually given labels to a binary class.
    '''
    if label == 'controversial':
        return 1
    return 0

def unsure(data=None):
    '''
    implements the /controversial endpoint. 

    parameters
    ----
    data: labeled

    returns
    --- 

    {
        controversial    : estimates,
        noncontroversial : estimates

    }

    CHANGED CODE HERE: We'll use active learning to search for new datapoints.
    Two scenarios are possible:
    1) If a data point _and_ label are given, it will update the training set and retrain the model.
    2) If no data point is given, it will search for a new data point to code and return this.
    '''
    if data:
        ''' expects an object like: {'nounphrase': {'label':'controversial'/'noncrontroversial','ip':'127.0.01'}}'''
        data = json.loads(data)
        '''get the topic name'''
        ## Python 2.7 3.5 difference here!
        # Python 3.5 use
        name = list(data.keys())[0]
        # Python 2.7 use
        # name = data.keys()[0]
        '''get the label'''
        label = convert_label(data[name]['label'])
        '''get the position of the topic in the training set'''
        ask_id = names.index(name)
        '''update training set with new label'''
        trn_ds.update(ask_id, label)
        '''retrain model'''
        model.train(trn_ds)
        
    else:
        '''
        When asked for a new data point, we call the UncertaintySampling method
        and write the name of this topic to JSON file
        '''
        ask_id = qs.make_query()
        results = { 'unsure' : names[ask_id] }
       
        return json.dumps(results)

def controversial():
    '''
    implements the /controversial endpoint. 

    parameters
    ----
    none

    returns
    --- 

    {
        controversial    : estimates,
        noncontroversial : estimates
    }
    
    This function returns the ten most controversial and non controversial topic based on the current model.
    '''

    labeled_features = trn_ds.get_labeled_entries()
    positions = [i for i,a in enumerate(trn_ds.data) if trn_ds.data[i][1] != None]
    datapoints = []
    for p in positions:
      datapoints.append(
                      {
                      'anchor' : names[p],
                      'score':model.predict(X[p])[0],
                      # Get confidence for class one, i.e. the topic being controversial
                      'confidence':model.predict_real(X[p])[0][1]
                          } 
                  )
    datapoints_sorted = sorted(datapoints, key=lambda x: (x['confidence']),reverse=True)
    controversial    = datapoints_sorted[:10]
    noncontroversial = datapoints_sorted[-10:]
    results = {'controversial':controversial, 'noncontroversial':noncontroversial}
    return results



if __name__=='__main__':

  input = sys.argv[1:]
  task = input[0]

  if task == 'anchor' and len(input) == 3:
    # return anchor

    seed = input[1]
    anchor = input[2]

    try:
      anchor = Anchor.get(id=anchor)
      instances = anchor.getInstances()
      print json.dumps(instances)
    except:
      print json.dumps([])



  if task == 'article' and len(input) == 3:
    # return article

    seed = input[1]
    article = input[2]

    try:
      article = Article.get(id=article)
      print json.dumps(vars(article), default=str)
    except:
      print json.dumps([])


  if task == 'controversial':

    ## DEMO ##
    # Initialize the model
    X,y,names = load_anchors()

    #X,y,names = load_anchors()
    model,trn_ds = initialize_model(X,y)
    qs = UncertaintySampling(trn_ds, method='lc', model=LogisticRegression())
    # Cell used for simulation, we randomly annotate words as being controversial or not 
    # During each iteration we update the model.
    # Lastly we call the 'controversial' function and sort all topics as controversial
    # or not based on the confidence score returned by the logistic regression
    import warnings
    warnings.filterwarnings('ignore')

    n_turns = 10
    answers = ['noncontroversial','controversial']*int(n_turns/2)
    random.shuffle(answers)
  #  for t in range(n_turns):
  #    result = unsure()
  #    labeled = {json.loads(result)['unsure']:{'label':answers[t],'ip':'127.0.01'}}
  #    unsure(json.dumps(labeled)) 

    controversies = controversial()
    print(json.dumps(controversies))

