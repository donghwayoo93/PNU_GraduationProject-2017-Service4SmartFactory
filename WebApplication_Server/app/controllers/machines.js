var Machine = require('../models/machine');

exports.getMachineInfo = function(req, res) {
    Machine.find({
        nearWorkerID: req.query.workerID
    }, {
        _id: 0,
        machineID: 1,
        name: 1,
        accessLevel: 1
    }, function(err, machineData) {
        if (err) {
            res.send(err);
        }
        if (!machineData) return res.status(404).send({
            err: "User not Found"
        });
        res.json(machineData);
    });
}

exports.getSensorData = function(req, res) {
    Machine.find({
        nearWorkerID: req.query.workerID
    }, {
        _id: 0,
        sensorState: 1
    }, (err, sensorData) => {
        if (err) {
            res.send(err);
        }
        if (!sensorData) return res.status(404).send({
            err: "Sensor data not Found"
        });
        res.json(sensorData);
    });
}

exports.getManual = function(req, res) {
    var manualNum = 0;
    // 0 : 이상 없음
    // 1 : solar가 높음
    // 2 : solar가 낮음
    // 3 : photosynthetic가 높음
    // 4 : photosynthetic가 낮음
    Machine.find({
        nearWorkerID: req.query.workerID
    }, {
        _id: 0,
        sensorState: 1
    }, (err, sensorData) => {
        var solar = sensorData[0].sensorState.solar;
        var photosynthetic = sensorData[0].sensorState.photosynthetic;
        if (solar > 1000) {
            //너무 밝다
            manualNum = 1;
        } else if (solar < 200) {
            //너무 어둡다
            manualNum = 2;
        }
        if (photosynthetic > 100) {
            //너무 밝다
            manualNum = 3;
        } else if (photosynthetic < 20) {
            //너무 어둡다
            manualNum = 4;
        }
        Machine.find({
            nearWorkerID: req.query.workerID
        }, {
            _id: 0,
            sensorState: 0,
            num: 0,
            accessLevel: 0,
            manual: {
                $elemMatch: {
                    num: String(manualNum)
                }
            }
        }, (err, manualData) => {
            if (err) {
                res.send(err);
            }
            if (!manualData) {
                console.log("아무것도 찾지 못함");
                //a = [{ "manual": [{ "instruction": ["현재 할당된 지시사항이 없습니다."] }] }]
                return res.status(404).send({
                    err: "manual data not Found"
                });
                //res.json(a);
            }
            res.json(manualData);
        });
    })

}