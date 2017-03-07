var express = require('express');
_ = require('underscore')._
var request = require('request');
var router = express.Router({mergeParams: true});
var exec = require('child_process').exec;
var path = require('path');
var parentDir = path.resolve(process.cwd());


router.get('/', function(req, res, next) {
    res.json({'info' : 'This is the ControCurator API v0.1'});
});

module.exports = router;
