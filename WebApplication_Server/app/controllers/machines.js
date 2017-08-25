var Machine = require('../models/machine');

exports.getMachineAllData = function(req, res, next) {
    Machine.find(function(err, machines) {
        if (err) {
            res.send(err);
        }
        if (!machines.length) return res.status(404).send({ err: "Machine not found" });
        res.send("User find successfully:\n" + machines);
        //res.json(machines);

    });
}

exports.getMachineInfo = function(req, res) {
    Machine.find({ nearWorkerID: req.query.workerID }, { _id: 0, machineID: 1, name: 1, accessLevel: 1 }, function(err, machineData) {
        if (err) {
            res.send(err);
        }
        if (!machineData) return res.status(404).send({ err: "User not Found" });
        res.json(machineData);
    });
}

exports.getSensorData = function(req, res) {
    Machine.find({ nearWorkerID: req.query.workerID }, { _id: 0, sensorState: 1 }, function(err, sensorData) {
        if (err) {
            res.send(err);
        }
        if (!sensorData) return res.status(404).send({ err: "Sensor data not Found" });
        res.json(sensorData);
    });
}

exports.getManual = function(req, res) {
    Machine.find({ nearWorkerID: req.query.workerID }, { _id: 0, sensorState: 0, num: 0, manual: { $elemMatch: { num: req.query.manualNum } } }, function(err, manualData) {
        if (err) {
            res.send(err);
        }
        if (!manualData) {
            console.log("아무것도 찾지 못함");
            //a = [{ "manual": [{ "instruction": ["현재 할당된 지시사항이 없습니다."] }] }]
            return res.status(404).send({ err: "manual data not Found" });
            //res.json(a);
        }
        res.json(manualData);
    });
}