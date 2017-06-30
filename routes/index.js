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

		var ip = req.connection.remoteAddress;
		client.create({
		  index: 'controcurator',
		  type: 'log',
		  id: md5(new Date()+ip+req.originalUrl),
		  body: {
			'agent'		: ip,
			'action' 	: 'view',
			'entity' 	: 'index',
			'timestamp'	: new Date(),
			'location'	: req.originalUrl,
			'data'		: {}
		}
		});



		var page = req.query.page;
		if(page === undefined) {
			page = 1;
		}

		var perpage = 20;
		var total = 4373;
		var pages = Math.ceil(total / perpage);
		var pagelist = pagination(page, pages);
		var from = (page - 1) * perpage;

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
				"from" : from,
				"size": perpage,
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
					"from" : from,
					"size": perpage,
					"sort": {
						"features.controversy.value": "asc"
					}
				}
				}).then(function (resp) {
						var bottom = resp.hits.hits;


						res.render('index', {'top': top, 'bottom': bottom, 'pages':pagelist,'current':page});


				}, function (err) {
						console.trace(err.message);
				});


		}, function (err) {
				console.trace(err.message);
		});

	
});

module.exports = router;
