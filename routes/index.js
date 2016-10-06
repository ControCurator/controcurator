var express = require('express');
_ = require('underscore')._
var request = require('request');
var router = express.Router();

//var search = require('../controllers/search');

/* GET home page. */

var summarize = function(str) {
    var ind = str.indexOf('<h3>');
    return str.substr(0, ~ind ? ind : 200);
}

function loadSearch() {
    return function(req, res, next) {

        req.positive = [];
        req.negative = [];
        req.neutral = [];

        var url = 'http://controcurator.org/ess/vaccination/topic/_search';
        var query = {
            "query" : {
                "constant_score" : { 
                    "filter" : {
                        "term" : { 
                            "sentiment" : "positive"
                        }
                    }
                }
            }
        };

         request({ uri: url, json: true, body: query }, function(err, resp, data) {
            if (err) {
                next();
            }// return res.sendStatus(500);
            req.positive = data.hits.hits;
            //next();
        });

        var url = 'http://controcurator.org/ess/vaccination/topic/_search';
        var query = {
            "query" : {
                "constant_score" : { 
                    "filter" : {
                        "term" : { 
                            "sentiment" : "negative"
                        }
                    }
                }
            }
        };

        request({ uri: url, json: true, body: query }, function(err, resp, data) {
            if (err) {
                next();
            }// return res.sendStatus(500);
            req.negative = data.hits.hits;
            //next();
        });

        var url = 'http://controcurator.org/ess/vaccination/topic/_search';
        var query = {
            "query" : {
                "constant_score" : { 
                    "filter" : {
                        "term" : { 
                            "sentiment" : "neutral"
                        }
                    }
                }
            }
        };

        request({ uri: url, json: true, body: query }, function(err, resp, data) {
            if (err) {
                next();
            }// return res.sendStatus(500);
            req.neutral = data.hits.hits;
            next();
        });
    };
}

router.get('/', loadSearch(), function(req, res, next) {
    res.render('index', { 'title':'ControCurator', q: req.query.q, results: req});
});

module.exports = router;
