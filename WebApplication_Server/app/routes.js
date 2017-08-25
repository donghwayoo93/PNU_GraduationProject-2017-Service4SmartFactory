var AuthenticationController = require('./controllers/authentication'),
    MachineController = require('./controllers/machines'),
    express = require('express'),
    passportService = require('../config/passport'),
    passport = require('passport');

var requireAuth = passport.authenticate('jwt', { session: false }),
    requireLogin = passport.authenticate('local', { session: false });

module.exports = function(app) {

    var apiRoutes = express.Router(),
        authRoutes = express.Router(),
        machineRoutes = express.Router();

    // Auth Routes
    apiRoutes.use('/auth', authRoutes);

    authRoutes.post('/register', AuthenticationController.register);
    authRoutes.post('/login', requireLogin, AuthenticationController.login);

    authRoutes.get('/protected', requireAuth, function(req, res) {
        res.send({ content: 'Success' });
    });

    // machines
    apiRoutes.use('/machines', machineRoutes);

    machineRoutes.get('/info', MachineController.getMachineInfo);
    machineRoutes.get('/sensor', MachineController.getSensorData);
    machineRoutes.get('/manual', MachineController.getManual);

    // Set up routes
    app.use('/api', apiRoutes);

}