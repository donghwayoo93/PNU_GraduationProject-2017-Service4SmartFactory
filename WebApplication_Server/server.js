var express = require('express');
var app = express();
var mongoose = require('mongoose');
var logger = require('morgan');
var bodyParser = require('body-parser');
var cors = require('cors');
var queue = require('express-queue');



var databaseConfig = require('./config/database');
var router = require('./app/routes');

mongoose.connect(databaseConfig.url);

app.listen(process.env.PORT || 8088);
console.log("App listening on port 8088");

app.use(queue({ activeLimit: 1 }));
app.use(bodyParser.urlencoded({ extended: false })); // Parses urlencoded bodies
app.use(bodyParser.json()); // Send JSON responses
app.use(logger('dev')); // Log requests to API using morgan
app.use(cors());

router(app);