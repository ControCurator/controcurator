var express = require('express');
_ = require('underscore')._
var request = require('request');
var router = express.Router({mergeParams: true});

//var search = require('../controllers/search');

/* GET home page. */

var summarize = function(str) {
    var ind = str.indexOf('<h3>');
    return str.substr(0, ~ind ? ind : 200);
}

function loadSearch() {
    return function(req, res, next) {
    	
        var url = 'http://controcurator.org/ess/crowdynews/webpage/_search?q='+req.params.id;
        req.searchResults = [];
        request({ uri: url, json: true }, function(err, resp, data) {
            if (err) return res.sendStatus(500);
            req.searchResults = data.hits.hits;
            next();
        });
    };
}

router.get('/', loadSearch(), function(req, res, next) {
    res.render('search', { 'title':'ControCurator', q: req.params.id, results: req.searchResults});
});

module.exports = router;
