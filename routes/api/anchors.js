var express = require('express');
_ = require('underscore')._
var request = require('request');
var router = express.Router({mergeParams: true});
var exec = require('child_process').exec;
var path = require('path');
var parentDir = path.resolve(process.cwd());


function getData() {
    return function(req, res, next) {
        var id = req.params.id;
        var task = req.params.task;
        console.log('python '+parentDir+'/python_code/endpoints.py '+task+' '+id)
        var child = exec('python '+parentDir+'/python_code/endpoints.py '+task+' '+id, {maxBuffer: 1024 * 500}, function(err, stdout, stderr) {
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

router.get('/', function(req, res, next) {
    res.json({'query' : req.params,
			'results' : req.data});
});

module.exports = router;
