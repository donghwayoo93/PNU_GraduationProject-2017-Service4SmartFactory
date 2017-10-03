// Set up
var express = require('express');
var app = express();
var logger = require('morgan');
var bodyParser = require('body-parser');
var cors = require('cors');
var pythonShell = require('python-shell');
var queue = require('express-queue');

app.use(queue({ activeLimit: 1 }));
app.use(bodyParser.urlencoded({ extended: false })); // Parse urlencoded bodies
app.use(bodyParser.json()); // Send JSON responses
app.use(logger('dev')); // Log requests to API using morgan
app.use(cors());

const FILENAME = "localSocket.py";
// Routes

app.post('/api/requestLogin', function(req, res) {
    //console.log(req.body);
    var options = {
        mode: 'text',
        pythonPath: '',
        pythonOptions: ['-u'],
        scriptPath: '',
        args: ['login', req.body.email, req.body.password]
    };
    pythonShell.run(FILENAME, options, function(err, results) {
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

app.get('/api/machines/info', function(req, res) {
    //console.log(req.body);
    var options = {
        mode: 'text',
        pythonPath: '',
        pythonOptions: ['-u'],
        scriptPath: '',
        args: ['machineInfo']
    };
    pythonShell.run(FILENAME, options, function(err, results) {
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

app.get('/api/machines/sensor', function(req, res) {
    //console.log(req.body);
    var options = {
        mode: 'text',
        pythonPath: '',
        pythonOptions: ['-u'],
        scriptPath: '',
        args: ['machineSensor']
    };
    pythonShell.run(FILENAME, options, function(err, results) {
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

app.get('/api/machines/manual', function(req, res) {
    //console.log(req.body);
    var options = {
        mode: 'text',
        pythonPath: '',
        pythonOptions: ['-u'],
        scriptPath: '',
        args: ['machineManual']
    };
    pythonShell.run(FILENAME, options, function(err, results) {
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

app.get('/api/machines/motorOn', function(req, res) {
    //console.log(req.body);
    var options = {
        mode: 'text',
        pythonPath: '',
        pythonOptions: ['-u'],
        scriptPath: '',
        args: ['machineMotor', 'ON']
    };
    pythonShell.run(FILENAME, options, function(err, results) {
        if (err) throw err;
        if (results == 'Unauthorized') {
            //console.log('Unauthorized 확인');
            //console.log(results);
            res.status(401).send(results);
        } else {
            res.send(results);
        }
    });
});

app.get('/api/machines/motorOff', function(req, res) {
    //console.log(req.body);
    var options = {
        mode: 'text',
        pythonPath: '',
        pythonOptions: ['-u'],
        scriptPath: '',
        args: ['machineMotor', 'OFF']
    };
    pythonShell.run(FILENAME, options, function(err, results) {
        if (err) throw err;
        if (results == 'Unauthorized') {
            //console.log('Unauthorized 확인');
            //console.log(results);
            res.status(401).send(results);
        } else {
            res.send(results);
        }
    });
});

app.get('/api/connect', function(req, res) {
    //console.log(req.body);
    var options = {
        mode: 'text',
        pythonPath: '',
        pythonOptions: ['-u'],
        scriptPath: '',
        args: ['connect']
    };
    pythonShell.run(FILENAME, options, function(err, results) {
        if (err) throw err;
        if (results == 'Unauthorized') {
            //console.log('Unauthorized 확인');
            //console.log(results);
            res.status(401).send(results);
        } else {
            res.send(results);
        }
    });
});

app.get('/api/disconnect', function(req, res) {
    //console.log(req.body);
    var options = {
        mode: 'text',
        pythonPath: '',
        pythonOptions: ['-u'],
        scriptPath: '',
        args: ['disconnect']
    };
    pythonShell.run(FILENAME, options, function(err, results) {
        if (err) throw err;
        if (results == 'Unauthorized') {
            //console.log('Unauthorized 확인');
            //console.log(results);
            res.status(401).send(results);
        } else {
            res.send(results);
        }
    });
});

app.get('/api/rssi', function(req, res) {
    //console.log(req.body);
    var options = {
        mode: 'text',
        pythonPath: '',
        pythonOptions: ['-u'],
        scriptPath: '',
        args: ['rssi']
    };
    pythonShell.run(FILENAME, options, function(err, results) {
        if (err) throw err;
        if (results == 'Unauthorized') {
            //console.log('Unauthorized 확인');
            //console.log(results);
            res.status(401).send(results);
        } else {
            res.send(results);
        }
    });
});

app.get('/api/sensorGauge', function(req, res) {
    //console.log(req.body);
    var options = {
        mode: 'text',
        pythonPath: '',
        pythonOptions: ['-u'],
        scriptPath: '',
        args: ['sensorGauge']
    };
    pythonShell.run(FILENAME, options, function(err, results) {
        if (err) throw err;
        if (results == 'Unauthorized') {
            //console.log('Unauthorized 확인');
            //console.log(results);
            res.status(401).send(results);
        } else {
            res.send(results);
        }
    });
});


// listen
var server = app.listen(9999);
server.setTimeout(51000);
console.log("App listening on port 9999");