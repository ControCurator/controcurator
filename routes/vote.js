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

router.get('/', function(req, res, next) {
    res.json({'info' : 'This isnt allowed.'});
});

router.post('/',function(req,res, next) {
    var input = req.body;
    var ip = req.connection.remoteAddress;

    var data = {'vote':input.vote}
    if('comment' in input) {
        data.comment = input.comment;
    }

      client.create({
        index: 'controcurator',
        type: 'log',
        id: md5(new Date()+ip+req.originalUrl),
        body: {
        'agent'   : ip,
        'action'  : 'vote',
        'entity'  : input.entity,
        'timestamp' : new Date(),
        'location'  : input.location,
        'data'    : data
      }
      });

    
});
module.exports = router;
