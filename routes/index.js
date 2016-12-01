var express = require('express');
_ = require('underscore')._
var request = require('request');
var router = express.Router();
var exec = require('child_process').exec;
var path = require('path');
var parentDir = path.resolve(process.cwd());

//var search = require('../controllers/search');

/* GET home page. */

var summarize = function(str) {
    var ind = str.indexOf('<h3>');
    return str.substr(0, ~ind ? ind : 200);
}

function loadSearch() {
    return function(req, res, next) {

  
        var child = exec('python '+parentDir+'/python_code/endpoints.py controversial', function(err, stdout, stderr) {
            if (err) console.log(err);
            else {
                //console.log(stdout);
                req.data = JSON.parse(stdout);
                //console.log(req.data.controversial);
                next();
            }
        });

    };
}

router.get('/', loadSearch(), function(req, res, next) {
    res.render('index', { 'title':'ControCurator', q: req.query.q, results: req.data});
});

module.exports = router;
