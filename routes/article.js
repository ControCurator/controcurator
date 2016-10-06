var express = require('express');
_ = require('underscore')._
var request = require('request');
var router = express.Router({mergeParams: true});

//var search = require('../controllers/search');

/* GET home page. */

function loadSearch() {
    return function(req, res, next) {
    	
        var url = 'http://controcurator.org/ess/vaccination/article/'+req.params.id;
        req.searchResults = [];
        request({ uri: url, json: true }, function(err, resp, data) {
            if (err) {
                //return res.sendStatus(500);
                next();
            }
            req.searchResults = data;
        });

        var url = 'http://controcurator.org/ess/vaccination/topic/_search';
        var query = {
            "query" : {
                "constant_score" : { 
                    "filter" : {
                        "term" : { 
                            "document_id" : req.params.id
                        }
                    }
                }
            }
        };

        request({ uri: url, json: true, body: query}, function(err, resp, data) {
            if (err) return res.sendStatus(500);
            req.searchResults.terms = data.hits.hits;
            var text = req.searchResults._source.text;
            //console.log(req.searchResults.terms);
            //term = data.hits.hits[0];
            var html = text;
            var terms = req.searchResults.terms;
            terms = terms.sort(function(a,b) {
              return b._source.text.length-a._source.text.length;
            });
            //console.log(terms);
            for(var i = 0; i < terms.length; i++) {
                term = terms[i]._source.text;
                sentiment = terms[i]._source.sentiment;
                html = html.replace(new RegExp(term, 'g'),'<a href="/search/'+term+'" class="ui term '+sentiment+' haspopup" data-content="blap">'+term+'</a>');
                
            }
            req.searchResults.content = html;


            next();
        });
    };
}


router.get('/', loadSearch(), function(req, res, next) {
    res.render('article', { 'title':'ControCurator', id: req.params.id, results: req.searchResults});
});

module.exports = router;
