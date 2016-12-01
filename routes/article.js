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

        var child = exec('python '+parentDir+'/python_code/endpoints.py article '+id, function(err, stdout, stderr) {
            if (err) console.log(err);
            else {

                var data = JSON.parse(stdout);
                var html = data.sentences;

                for(var e in data.entities) {
                    for(var s in data.entities[e]) {
                        var score = data.entities[e][s]['sentiment']['score'];
                        var label = data.entities[e][s]['label'];
                        if(score > 0.2) {
                            sentiment = 'positive';
                        } else if (score < 0.2) {
                            sentiment = 'negative';
                        } else {
                            sentiment = 'neutral';
                        }
                        html[s] = html[s].replace(new RegExp(label, 'g'),'<a href="/browse/anchor/'+e+'" class="ui term '+sentiment+' haspopup" data-content="blap">'+label+'</a>');

                    }
                }

                data.html = html.join(' ');
                req.data = data;
                next();
            }
        });

    };
}


router.get('/', loadSearch(), function(req, res, next) {
    res.render('article', { 'title':'ControCurator', 'id': req.params.id, results: req.data});
});

module.exports = router;
