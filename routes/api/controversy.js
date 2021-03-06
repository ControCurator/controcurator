var express = require('express');
_ = require('underscore')._
var request = require('request');
var router = express.Router({mergeParams: true});
var exec = require('child_process').exec;
var path = require('path');
var parentDir = path.resolve(process.cwd());


function getData() {
    return function(req, res, next) {
        if (req.params.id) {
            var id = ' '+req.params.id;
        }
        else {
            var id = '';
        }
        console.log('python '+parentDir+'/controllers/controversy.py')
        var child = exec('python '+parentDir+'/controllers/controversy.py'+id, {maxBuffer: 1024 * 500}, function(err, stdout, stderr) {
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
    res.json({'query' : req.params,
			'results' : req.data});
});

module.exports = router;
