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


function secondsToTime(t)
{
    var d = Math.floor(t/86400),
        h = ('0'+Math.floor(t/3600) % 24).slice(-2),
        m = ('0'+Math.floor(t/60)%60).slice(-2),
        s = ('0' + t % 60).slice(-2);
    return (d>0?d:0);
//    return (d>0?d+'d ':'')+(h>0?h+':':'')+(m>0?m+':':'')+(t>60?s:s+'s');
}

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



router.post('/', function(req, res, next) {
    // article
    var id = req.params.id;

    var input = req.body;
    var ip = req.connection.remoteAddress;

    var data = {'annotations' : input}
    
      client.create({
        index: 'controcurator',
        type: 'log',
        id: md5(new Date()+ip+req.originalUrl+'annotate'),
        body: {
        'agent'   : ip,
        'action'  : 'vote',
        'entity'  : input.entity,
        'timestamp' : new Date(),
        'location'  : input.location,
        'data'    : data
      }
      });
    



    var ip = req.connection.remoteAddress;
    client.create({
      index: 'controcurator',
      type: 'log',
      id: md5(new Date()+ip+req.originalUrl),
      body: {
        'agent'     : ip,
        'action'    : 'view',
        'entity'    : 'article',
        'timestamp' : new Date(),
        'location'  : req.originalUrl,
        'data'      : {}
    }
    });





    client.get({
      index: 'controcurator',
      type: 'article',
      id: id
    }).then(function (resp) {
        //console.log(resp);
        var article = resp._source;

        /*
        var stats = {}
        stats['actors'] = 15;//Array.from(new Set(article.comments.map(function (x) { return x.author; }))).length;
        stats['comments'] = article.comments.length;
        stats['times'] = article.comments.map(function (x) { return new Date(x.timestamp).getTime(); })
        stats['times'].push(new Date(article.published).getTime());
        stats['times'] = stats['times'].sort(function(a,b){return a - b});
        stats['duration'] = stats['times'][stats['times'].length-1] - stats['times'][0];
        stats['duration'] = secondsToTime(stats['duration']);
        */

        var stats = article.features.controversy;


        var positive = article.comments.slice(0);
        positive = positive.filter(function(a) {
            return a.sentiment.sentiment > 0;
        });
        positive.sort(function(a,b) {
            return b.sentiment.sentiment - a.sentiment.sentiment;
        });

        var negative = article.comments.slice(0);
        negative = negative.filter(function(a) {
            return a.sentiment.sentiment < 0;
        });
        negative.sort(function(a,b) {
            return a.sentiment.sentiment - b.sentiment.sentiment;
        });

        var commentCount = Math.max(positive.length,negative.length);

        var page = req.query.page;
        if(page === undefined) {
            page = 1;
        }

        var perpage = 5;
        var total = commentCount;
        var pages = Math.ceil(total / perpage);
        if(pages < 2) {
            pagelist = [1]
        } else {
            var pagelist = pagination(page, pages);
        }
        var from = (page - 1) * perpage;

        positive = positive.slice(from, from + perpage);
        negative = negative.slice(from, from + perpage);


        article.features.clusters.forEach(function (x,i) {
            article.features.clusters[i]['name'] = article.features.clusters[i]['name'].replace(/_/g,' ');
        });
        res.render('article', {'id' : id, 'article': article, 'positive' : positive, 'negative' : negative, 'stats':stats, 'pages':pagelist, 'current':page});

    }, function (err) {
        console.trace(err.message);
        res.render('article', {'id' : id, 'notfound':1,'annotated':true});
    });

});


router.get('/', function(req, res, next) {
    // article
    var id = req.params.id;

    var ip = req.connection.remoteAddress;
    client.create({
      index: 'controcurator',
      type: 'log',
      id: md5(new Date()+ip+req.originalUrl),
      body: {
        'agent'     : ip,
        'action'    : 'view',
        'entity'    : 'article',
        'timestamp' : new Date(),
        'location'  : req.originalUrl,
        'data'      : {}
    }
    });





    client.get({
      index: 'controcurator',
      type: 'article',
      id: id
    }).then(function (resp) {
        //console.log(resp);
        var article = resp._source;

        /*
        var stats = {}
        stats['actors'] = 15;//Array.from(new Set(article.comments.map(function (x) { return x.author; }))).length;
        stats['comments'] = article.comments.length;
        stats['times'] = article.comments.map(function (x) { return new Date(x.timestamp).getTime(); })
        stats['times'].push(new Date(article.published).getTime());
        stats['times'] = stats['times'].sort(function(a,b){return a - b});
        stats['duration'] = stats['times'][stats['times'].length-1] - stats['times'][0];
        stats['duration'] = secondsToTime(stats['duration']);
        */

        var stats = article.features.controversy;


        var positive = article.comments.slice(0);
        positive = positive.filter(function(a) {
            return a.sentiment.sentiment > 0;
        });
        positive.sort(function(a,b) {
            return b.sentiment.sentiment - a.sentiment.sentiment;
        });

        var negative = article.comments.slice(0);
        negative = negative.filter(function(a) {
            return a.sentiment.sentiment < 0;
        });
        negative.sort(function(a,b) {
            return a.sentiment.sentiment - b.sentiment.sentiment;
        });

        var commentCount = Math.max(positive.length,negative.length);

        var page = req.query.page;
        if(page === undefined) {
            page = 1;
        }

        var perpage = 5;
        var total = commentCount;
        var pages = Math.ceil(total / perpage);
        if(pages < 2) {
            pagelist = [1]
        } else {
            var pagelist = pagination(page, pages);
        }
        var from = (page - 1) * perpage;

        positive = positive.slice(from, from + perpage);
        negative = negative.slice(from, from + perpage);


        article.features.clusters.forEach(function (x,i) {
            article.features.clusters[i]['name'] = article.features.clusters[i]['name'].replace(/_/g,' ');
        });
        res.render('article', {'id' : id, 'article': article, 'positive' : positive, 'negative' : negative, 'stats':stats, 'pages':pagelist, 'current':page});

    }, function (err) {
        console.trace(err.message);
        res.render('article', {'id' : id, 'notfound':1});
    });

});

module.exports = router;
