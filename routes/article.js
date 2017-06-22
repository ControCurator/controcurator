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

function secondsToTime(t)
{
	var d = Math.floor(t/86400),
		h = ('0'+Math.floor(t/3600) % 24).slice(-2),
		m = ('0'+Math.floor(t/60)%60).slice(-2),
		s = ('0' + t % 60).slice(-2);
	return (d>0?d+' days ':'');
//    return (d>0?d+'d ':'')+(h>0?h+':':'')+(m>0?m+':':'')+(t>60?s:s+'s');
}

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

		var stats = {}
		stats['actors'] = 15;//Array.from(new Set(article.comments.map(function (x) { return x.author; }))).length;
		stats['comments'] = article.comments.length;
		stats['times'] = article.comments.map(function (x) { return new Date(x.timestamp).getTime(); })
		stats['times'].push(new Date(article.published).getTime());
		stats['times'] = stats['times'].sort(function(a,b){return a - b});
		stats['duration'] = stats['times'][stats['times'].length-1] - stats['times'][0];
		stats['duration'] = secondsToTime(stats['duration']);
		


		var positive = article.comments.slice(0);
		positive = positive.filter(function(a) {
			return a.sentiment.sentiment > 0;
		});
		positive.sort(function(a,b) {
			return b.sentiment.sentiment - a.sentiment.sentiment;
		});
		positive = positive.slice(0, 5);

		var negative = article.comments.slice(0);
		negative = negative.filter(function(a) {
			return a.sentiment.sentiment < 0;
		});
		negative.sort(function(a,b) {
			return a.sentiment.sentiment - b.sentiment.sentiment;
		});
		negative = negative.slice(0, 5);

		res.render('article', {'id' : id, 'article': article, 'positive' : positive, 'negative' : negative, 'stats':stats});

	}, function (err) {
		console.trace(err.message);
		res.render('article', {'id' : id, 'notfound':1});
	});

});

module.exports = router;
