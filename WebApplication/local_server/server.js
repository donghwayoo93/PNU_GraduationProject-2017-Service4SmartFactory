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
    console.log(req.body.email);
    console.log(req.body.password);
    var options = {
        mode: 'text',
        pythonPath: '',
        pythonOptions: ['-u'],
        scriptPath: '',
        args: [req.body.email, req.body.password, 'value3']
    };
    pythonShell.run('test.py', options, function(err, results) {
        if (err) throw err;
        results = JSON.parse(results);
        console.log('results: %j', results);
        res.send(results);
    });

});

app.get('/api/rooms/reserve', function(req, res) {

});

// listen
app.listen(9999);
console.log("App listening on port 9999");