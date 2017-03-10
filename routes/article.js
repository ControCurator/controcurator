var express = require('express');
_ = require('underscore')._
var request = require('request');
var router = express.Router({mergeParams: true});
var exec = require('child_process').exec;
var path = require('path');
var parentDir = path.resolve(process.cwd());

function loadSearch() {
    return function(req, res, next) {
    	
        var id = req.params.id;

        var child = exec('python '+parentDir+'/controllers/documents.py '+id, function(err, stdout, stderr) {
            if (err) console.log(err);
            else {

                var data = JSON.parse(stdout);
                req.data = data;
                console.trace(data)
                next();
            }
        });

    };
}


router.get('/', loadSearch(), function(req, res, next) {
    res.render('article', { 'title':'ControCurator', 'id': req.params.id, results: req.data});
});

module.exports = router;
