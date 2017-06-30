var express = require('express');
_ = require('underscore')._
var request = require('request');
var router = express.Router({mergeParams: true});
var exec = require('child_process').exec;
var path = require('path');
var parentDir = path.resolve(process.cwd());
var elasticsearch = require('elasticsearch');
var client = new elasticsearch.Client({
  host: 'http://controcurator.org/ess'
});
var md5 = require('md5');

function pagination(c, m) {
    "use strict";
    var current = parseInt(c),
        last = m-1,
        delta = 2,
        left = current-delta,
        right = current+delta+1,
        range = [],
        rangeWithDots = [],
        l;
  
    range.push(1)
    for (var i = current - delta; i <= current + delta; i++) {
        if (i >= left && i < right && i < m && i > 1) {
            range.push(i);
        }
    }  
    range.push(m);

    for (i in range) {
        if (l) {
            if (range[i] - l === 2) {
                rangeWithDots.push(l + 1);
            } else if (range[i] - l !== 1) {
                rangeWithDots.push('...');
            }
        }
        rangeWithDots.push(range[i]);
        l = range[i];
    }
    return rangeWithDots;
}


router.get('/', function(req, res, next) {




  var iframe = "http://controcurator.org/kibana/app/kibana#/visualize/create?embed=true&type=line&indexPattern=controcurator&_g=(refreshInterval:(display:Off,pause:!f,value:0),time:(from:'2016-10-01T15:55:27.190Z',mode:absolute,to:'2016-12-01T16:55:27.190Z'))&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'"+req.params.id+"')),uiState:(spy:(mode:(fill:!f,name:!n))),vis:(aggs:!((id:'1',params:(field:features.controversy.value),schema:metric,type:avg),(id:'2',params:(customInterval:'2h',extended_bounds:(),field:published,interval:d,min_doc_count:1),schema:segment,type:date_histogram)),listeners:(),params:(addLegend:!t,addTimeMarker:!f,addTooltip:!t,defaultYExtents:!t,drawLinesBetweenPoints:!t,interpolate:linear,radiusRatio:9,scale:linear,setYExtents:!t,shareYAxis:!t,showCircles:!f,smoothLines:!t,times:!(),yAxis:(max:1,min:0)),title:Controversy,type:line))"
  if(req.query.id) {
    req.params.id = req.query.id;
  }


  var ip = req.connection.remoteAddress;
  client.create({
    index: 'controcurator',
    type: 'log',
    id: md5(new Date()+ip+req.originalUrl),
    body: {
    'agent'   : ip,
    'action'  : 'view',
    'entity'  : 'search',
    'timestamp' : new Date(),
    'location'  : req.originalUrl,
    'data'    : {'search':req.params.id}
  }
  });


  var featuresquery = {
  "_source": {
    "includes": [
      "features.controversy"
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
            "features.controversy.openness": {
              "gt": "1"
            }
          }
        }
      ]
    }
  },
  "from": 0,
  "size": 1000
}



 





  request.post({
  url: 'http://controcurator.org/ess/controcurator/article/_search',
  json: featuresquery
  }, function (error, response, body) {
    if (!error && response.statusCode == 200) {
      var articles = body.hits.hits;

      var scores = articles.map(function (x) { return x._source.features.controversy.value });
      var positives = scores.filter(function(x) { return x >= 0.5; });
      var negatives = scores.filter(function(x) { return x < 0.5; });
      var count = Math.max(positives.length,negatives.length);

      var s = articles.map(function (x) { return x._source.features.controversy});
      s = s.filter(function(x) { return 'value' in x; });
      s = s.filter(function(x) { return 'duration' in x; });
      var stats = {
        'controversy' : s.map(function (x) { return x.value}),
        'actors': s.map(function (x) { return x.actors}),
        'polarity': s.map(function (x) { return x.polarity}),
        'openness': s.map(function (x) { return x.openness}),
        'persistence': s.map(function (x) { return x.duration}),
        'emotion': s.map(function (x) { return x.emotion})
      }

      stats['controversy'] = Math.max.apply(Math,stats['controversy']);
      var sum = stats['actors'].reduce(function(a, b) { return a + b; });
      stats['actors'] = sum / stats['actors'].length;
      stats['polarity'] = Math.max.apply(Math,stats['polarity']);
      var sum = stats['openness'].reduce(function(a, b) { return a + b; });
      stats['openness'] = sum / stats['openness'].length;      
      stats['persistence'] = Math.max.apply(Math,stats['persistence']);
      var sum = stats['emotion'].reduce(function(a, b) { return a + b; });
      stats['emotion'] = sum / stats['emotion'].length;

//      stats = stats.reduce(function (x) { return sum(x) / x.length});

      

      var page = req.query.page;
      if(page === undefined) {
        page = 1;
      }

      var perpage = 10;
      var total = count;
      var pages = Math.ceil(total / perpage);
      if(pages < 2) {
        pagelist = [1]
      } else {
        var pagelist = pagination(page, pages);
      }
      var from = (page - 1) * perpage;

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
            "from": from,
            "size": perpage,
            "sort": {
              "features.controversy.value": "desc"
            }
          }

    request.post({
    url: 'http://controcurator.org/ess/controcurator/article/_search',
    json: topquery
    }, function (error, response, body) {
      if (!error && response.statusCode == 200) {
        var top = body.hits.hits;



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
                  "from": from,
                  "size": perpage,
                  "sort": {
                    "features.controversy.value": "asc"
                  }
                }

        request.post({
        url: 'http://controcurator.org/ess/controcurator/article/_search',
        json: bottomquery
        }, function (error, response, body) {
          if (!error && response.statusCode == 200) {
            var bottom = body.hits.hits;



          
            res.render('search', { 'top': top, 'bottom': bottom,'search':req.params.id, 'iframe':iframe, 'pages':pagelist,'current':page,'stats':stats,});

          }
        });

      }
    });
  }
  });

  
});

module.exports = router;
