var express = require('express');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var rewrite = require('express-urlrewrite');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');

var index = require('./routes/index');
var article = require('./routes/article');
var anchor = require('./routes/anchor');
var search = require('./routes/search');
var users = require('./routes/users');
var api = require('./routes/api');
var vote = require('./routes/vote');
var api_documents = require('./routes/api/documents');
var api_anchors = require('./routes/api/anchors');
var api_controversy = require('./routes/api/controversy');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');
//app.use(rewrite(/^\/search\/\?q\=(\w+)/, '/search/$1'));

// uncomment after placing your favicon in /public
//app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));
app.use(logger('dev'));
app.use(bodyParser.json({limit: '20mb'}));
app.use(bodyParser.urlencoded({ extended: false, limit: '20mb',parameterLimit:100000 }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', index);
app.use('/anchor/:id', anchor);
app.use('/search/:id?', search);
app.use('/article/:id', article);
app.use('/users', users);
app.use('/api/', api);
app.use('/vote/', vote);
app.use('/api/documents/:id?', api_documents);
app.use('/api/anchors/:id?', api_anchors);
app.use('/api/controversy/:input?', api_controversy);


// catch 404 and forward to error handler
app.use(function(req, res, next) {
  var err = new Error('Not Found');
  err.status = 404;
  next(err);
});

// error handlers

// development error handler
// will print stacktrace
if (app.get('env') === 'development') {
  app.use(function(err, req, res, next) {
    res.status(err.status || 500);
    res.render('error', {
      message: err.message,
      error: err
    });
  });
}

// production error handler
// no stacktraces leaked to user
app.use(function(err, req, res, next) {
  res.status(err.status || 500);
  res.render('error', {
    message: err.message,
    error: {}
  });
});


module.exports = app;
