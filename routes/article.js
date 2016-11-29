var express = require('express');
_ = require('underscore')._
var request = require('request');
var router = express.Router({mergeParams: true});
var exec = require('child_process').exec;
var path = require('path');
var parentDir = path.resolve(process.cwd());

function loadSearch() {
    return function(req, res, next) {
    	
        var seed = req.params.seed;
        var id = req.params.id;

        var child = exec('python '+parentDir+'/python_code/endpoints.py article '+seed+' '+id, function(err, stdout, stderr) {
            if (err) console.log(err);
            else {
                req.data = JSON.parse(stdout);
                console.log(req.data.date)
                next();
            }
        });

    };
}


router.get('/', loadSearch(), function(req, res, next) {
    res.render('article', { 'title':'ControCurator', 'seed': req.params.seed, 'id': req.params.id, results: req.data});
});

module.exports = router;
