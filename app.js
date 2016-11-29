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
var users = require('./routes/users');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');
//app.use(rewrite(/^\/search\/\?q\=(\w+)/, '/search/$1'));

// uncomment after placing your favicon in /public
//app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', index);
app.use('/anchor/:seed/:id', anchor);
app.use('/article/:seed/:id', article);
app.use('/users', users);


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

var livereload = require('livereload');

// This is different form http.createServer() or app.createServer()
var reloadServer = livereload.createServer();

reloadServer.config.exts.push("jade");  // Enable live reload for jade files
reloadServer.watch(__dirname);  // Enable watch on complete app folder

// You can also enable watch on multiple folders:
reloadServer.watch([__dirname + "/js", __dirname + "/css"]);

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
