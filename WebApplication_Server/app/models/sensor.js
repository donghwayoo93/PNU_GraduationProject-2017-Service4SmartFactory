var mongoose = require('mongoose');

var sensorSchema = new mongoose.Schema({

    machineID: {
        type: String,
        unique: true
    },
    sensorState: {
        type: Array
    }
});

module.exports = mongoose.model('Sensor', sensorSchema);