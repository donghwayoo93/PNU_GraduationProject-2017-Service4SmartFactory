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

exports.getMachineData = function(req, res) {

    Machine.find({ "machineID": req.params.machineID }, function(err, machineData) {

        if (err) {
            res.send(err);
        }
        if (!machineData) return res.status(404).send({ err: "User not Found" });
        res.json(machineData);

    });

}

exports.getMachineManual = function(req, res, next) {
        Machine.find(function(err, machineManual) {
            if (err) {
                res.send(err);
            }
            res.json(machineManual);
        });
    }
    /**
    		exports.createTodo = function(req, res, next) {

    				Machine.create({
    						title: req.body.title
    				}, function(err, todo) {

    						if (err) {
    								res.send(err);
    						}

    						Machine.find(function(err, todos) {

    								if (err) {
    										res.send(err);
    								}

    								res.json(todos);

    						});

    				});

    		}

    		exports.deleteTodo = function(req, res, next) {

    				Machine.remove({
    						_id: req.params.todo_id
    				}, function(err, todo) {
    						res.json(todo);
    				});
    }
    */