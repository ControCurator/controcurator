var express = require('express');
_ = require('underscore')._
var request = require('request');
var router = express.Router({mergeParams: true});
var exec = require('child_process').exec;
var path = require('path');
var parentDir = path.resolve(process.cwd());

router.get('/', function(req, res, next) {

  var topquery = {
            "_source": {
              "excludes": [
                "comments"
              ]
            },
            "query": {
              "nested": {
                "path": "document",
                "score_mode": "avg",
                "query": {
                  "bool": {
                    "must": [
                      {
                        "match": {
                          "document.title": req.params.id
                        }
                      }
                    ]
                  }
                }
              }
            },
            "size": 5,
            "sort": {
              "features.controversy.random": "asc"
            }
          }


    var bottomquery = {
            "_source": {
              "excludes": [
                "comments"
              ]
            },
            "query": {
              "nested": {
                "path": "document",
                "score_mode": "avg",
                "query": {
                  "bool": {
                    "must": [
                      {
                        "match": {
                          "document.title": req.params.id
                        }
                      }
                    ]
                  }
                }
              }
            },
            "size": 5,
            "sort": {
              "features.controversy.random": "desc"
            }
          }

  request.post({
  url: 'http://controcurator.org/ess/controcurator/article/_search',
  json: topquery
  }, function (error, response, body) {
    if (!error && response.statusCode == 200) {
      var top = body.hits.hits;

      request.post({
      url: 'http://controcurator.org/ess/controcurator/article/_search',
      json: bottomquery
      }, function (error, response, body) {
        if (!error && response.statusCode == 200) {
          var bottom = body.hits.hits;
        
          res.render('index', { 'top': top, 'bottom': bottom});

        }
      });

    }
  });

  
});

module.exports = router;
