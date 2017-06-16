var express = require('express');
_ = require('underscore')._
var request = require('request');
var router = express.Router({mergeParams: true});
var exec = require('child_process').exec;
var path = require('path');
var parentDir = path.resolve(process.cwd());

router.get('/', function(req, res, next) {

  var iframe = "http://controcurator.org/kibana/app/kibana#/visualize/create?embed=true&type=line&indexPattern=controcurator&_g=(refreshInterval:(display:Off,pause:!f,value:0),time:(from:'2016-10-01T15:55:27.190Z',mode:absolute,to:'2016-12-01T16:55:27.190Z'))&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'"+req.params.id+"')),uiState:(spy:(mode:(fill:!f,name:!n))),vis:(aggs:!((id:'1',params:(field:features.controversy.value),schema:metric,type:avg),(id:'2',params:(customInterval:'2h',extended_bounds:(),field:published,interval:d,min_doc_count:1),schema:segment,type:date_histogram)),listeners:(),params:(addLegend:!t,addTimeMarker:!t,addTooltip:!f,defaultYExtents:!t,drawLinesBetweenPoints:!t,interpolate:linear,radiusRatio:9,scale:linear,setYExtents:!f,shareYAxis:!t,showCircles:!t,smoothLines:!t,times:!(),yAxis:()),title:'Controversy',type:line))"
  if(req.query.id) {
    req.params.id = req.query.id;
  }

  var topquery = {
            "_source": {
              "excludes": [
                "comments"
              ]
            },
            "query": {
              "bool": {
                "must": [
                {
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
                  {
                    "range": {
                      "features.controversy.value": {
                        "gte": "0.5"
                      }
                    }
                  }
                ]
              }
            },
            "size": 10,
            "sort": {
              "features.controversy.value": "desc"
            }
          }


    var bottomquery = {
            "_source": {
              "excludes": [
                "comments"
              ]
            },
            "query": {
              "bool": {
                "must": [
                {
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
                  {
                    "range": {
                      "features.controversy.value": {
                        "gt": "0",
                        "lt": "0.5"
                      }
                    }
                  }
                ]
              }
            },
            "size": 10,
            "sort": {
              "features.controversy.value": "asc"
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
        
          res.render('search', { 'top': top, 'bottom': bottom,'search':req.params.id, 'iframe':iframe});

        }
      });

    }
  });

  
});

module.exports = router;
