// Set up
var express = require('express');
var app = express();
var logger = require('morgan');
var bodyParser = require('body-parser');
var cors = require('cors');
var pythonShell = require('python-shell');

app.use(bodyParser.urlencoded({ extended: false })); // Parse urlencoded bodies
app.use(bodyParser.json()); // Send JSON responses
app.use(logger('dev')); // Log requests to API using morgan
app.use(cors());

// Routes

app.post('/api/requestLogin', function(req, res) {
    //console.log(req.body);
    var options = {
        mode: 'text',
        pythonPath: '',
        pythonOptions: ['-u'],
        scriptPath: '',
        args: [req.body.email, req.body.password]
    };
    pythonShell.run('test.py', options, function(err, results) {
        if (err) throw err;
        if (results == 'Unauthorized') {
            //console.log('Unauthorized 확인');
            //console.log(results);
            res.status(401).send(results);
        } else {
            results = JSON.parse(results);
            //console.log('results: %j', results);
            res.send(results);
        }

    });

});

// listen
app.listen(9999);
console.log("App listening on port 9999");