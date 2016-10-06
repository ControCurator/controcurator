var connection = require('../config/connection')

var summarize = function(str) {
    var ind = str.indexOf('<h3>');
    return str.substr(0, ~ind ? ind : 200);
}

var loadSearch = function(db) {
    return function(req, res, next) {
        var url = connection+db+'/'+db+'/_search?q='+req.query.q;
        req.searchResults = [];
        request({ uri: url, json: true }, function(err, resp, data) {
            if (err) return res.send(500);
            req.searchResults = _(data.hits.hits).map(function(hit) {
                return hit._source;
            });
            next();
        });
    };
}