var express = require('express');
_ = require('underscore')._
var request = require('request');
var router = express.Router();
var exec = require('child_process').exec;
var path = require('path');
var parentDir = path.resolve(process.cwd());


function getData() {
    return function(req, res, next) {
        var child = exec('python '+parentDir+'/controllers/barometer.py', {maxBuffer: 1024 * 500}, function(err, stdout, stderr) {
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

router.get('/', getData(), function(req, res, next) {
    res.render('index', { 'title':'ControCurator', results: req.data});
});

module.exports = router;
