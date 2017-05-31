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

router.post('/',function(req,res) {
    //try {
      //  var input = JSON.parse(req);
    //} catch (e) {
    //    res.json({'error':'Input was not valid JSON.'});
    //}
    var input = req;
    var amountofitems = input.length;
    var gooditems = 0;
    var baditems = 0;

    for (var i=0; i < amountofitems; i++)
    {
        var currentitem = input[i];
        if (!currentitem.hasOwnProperty('id') || !currentitem.hasOwnProperty('text'))
        {
            baditems++;
            continue;
        }
        gooditems++;
    }
    var controscore = Math.random();


    res.json({'controversy':controscore,'totalItems':amountofitems,'goodItems':gooditems,'badItems':baditems});

});
module.exports = router;
