var mongoose = require('mongoose');

var machineSchema = new mongoose.Schema({

    machineID: {
        type: String,
        unique: true
    },
    name: {
        type: String
    },
    accessLevel: {
        type: String,
        enum: ['1', '2', '3'],
        default: '1'
    },
    accessLevel: {
        type: String
    },
    sensorState: {
        type: Array
    },
    manual: {
        type: Array
    }
}, {
    timestamps: true
});

module.exports = mongoose.model('Machine', machineSchema);