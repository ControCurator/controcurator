var express = require('express');
_ = require('underscore')._
var request = require('request');
var router = express.Router({mergeParams: true});
var exec = require('child_process').exec;
var path = require('path');
var parentDir = path.resolve(process.cwd());
var PythonShell = require('python-shell');

router.get('/', function(req, res, next) {
    res.json({'info' : 'This is the ControCurator API v0.1'});
});

router.post('/',function(req,res, next) {
    var input = req.body;
    var amountofitems = input.length;

    var gooditems = 0;
    var baditems = 0;

    for (var i=0; i < amountofitems; i++)
    {
        var currentitem = input[i];
        if (!currentitem.hasOwnProperty('id') || !currentitem.hasOwnProperty('text')) //Test for an id and an actual body
        {
            baditems++;
            continue;
        }
        gooditems++;
    }

    var inputstring = JSON.stringify(input);
    //console.log('python '+parentDir+'/controllers/controversy.py '+inputstring)


    var pyshell = new PythonShell('/controllers/controversy.py');

    // sends a message to the Python script via stdin
    pyshell.send(inputstring);

    pyshell.on('message', function (message) {
      // received a message sent from the Python script (a simple "print" statement)
        res.json(message);

//            {'controversy':m['controversy'],'confidence':m['confidence'],'totalItems':amountofitems,'goodItems':gooditems,'badItems':baditems});
        
    });

    // end the input stream and allow the process to exit
    pyshell.end(function (err) {
        if (err) throw err;
      console.log('finished');
    });
    

    
});
module.exports = router;
