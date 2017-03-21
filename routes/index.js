var express = require('express');
_ = require('underscore')._
var request = require('request');
var router = express.Router();
var exec = require('child_process').exec;
var path = require('path');
var parentDir = path.resolve(process.cwd());
var elasticsearch = require('elasticsearch');
var client = new elasticsearch.Client({
  host: 'http://controcurator.org/ess'
});

router.get('/', function(req, res, next) {

    client.search({
      index: 'controcurator',
      type: 'article',
      body: 
      {
        "_source": {
          "excludes": [
            "comments"
          ]
        },
        "query": {
        "bool": {
          "must": [
            {
              "range": {
                "features.controversy.value": {
                  "gt": "0"
                }
              }
            }
          ]
        }
        },
        "size": 5,
        "sort": {
          "features.controversy.value": "desc"
        }
      }
    }).then(function (resp) {
        var top = resp.hits.hits;

        
        client.search({
          index: 'controcurator',
          type: 'article',
          body: 
          {
          "_source": {
            "excludes": [
              "comments"
            ]
          },
          "query": {
          "bool": {
            "must": [
              {
                "range": {
                  "features.controversy.value": {
                    "gt": "0"
                  }
                }
              }
            ]
          }
          },
          "size": 5,
          "sort": {
            "features.controversy.value": "asc"
          }
        }
        }).then(function (resp) {
            var bottom = resp.hits.hits;


            res.render('index', {'top': top, 'bottom': bottom});


        }, function (err) {
            console.trace(err.message);
        });


    }, function (err) {
        console.trace(err.message);
    });

  
});

module.exports = router;
