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

router.get('/', function(req, res, next) {

    // article
    var id = req.params.id;
    client.get({
      index: 'controcurator',
      type: 'article',
      id: id
    }).then(function (resp) {
        //console.log(resp);
        var article = resp._source;
        var positive = article.comments;
        var negative = article.comments;

        res.render('article', {'id' : id, 'article': article, 'positive' : positive, 'negative' : negative});

    }, function (err) {
        console.trace(err.message);
        res.render('article', {'id' : id, 'notfound':1});
    });

});

module.exports = router;
