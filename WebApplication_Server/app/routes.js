var AuthenticationController = require('./controllers/authentication'),
    TodoController = require('./controllers/todos'),
    MachineController = require('./controllers/machines'),
    express = require('express'),
    passportService = require('../config/passport'),
    passport = require('passport');

var requireAuth = passport.authenticate('jwt', { session: false }),
    requireLogin = passport.authenticate('local', { session: false });

module.exports = function(app) {

    var apiRoutes = express.Router(),
        authRoutes = express.Router(),
        todoRoutes = express.Router(),
        machineRoutes = express.Router();

    // Auth Routes
    apiRoutes.use('/auth', authRoutes);

    authRoutes.post('/register', AuthenticationController.register);
    authRoutes.post('/login', requireLogin, AuthenticationController.login);

    authRoutes.get('/protected', requireAuth, function(req, res) {
        res.send({ content: 'Success' });
    });

    // Todo Routes
    apiRoutes.use('/todos', todoRoutes);

    todoRoutes.get('/', requireAuth, AuthenticationController.roleAuthorization(['reader', 'creator', 'editor']), TodoController.getTodos);
    todoRoutes.post('/', requireAuth, AuthenticationController.roleAuthorization(['creator', 'editor']), TodoController.createTodo);
    todoRoutes.delete('/:todo_id', requireAuth, AuthenticationController.roleAuthorization(['editor']), TodoController.deleteTodo);

    // machines
    apiRoutes.use('/machines', machineRoutes);

    machineRoutes.get('/', MachineController.getMachineAllData);
    machineRoutes.get('/machinesData/:machineID', MachineController.getMachineData);
    //machineRoutes.get('/machinesManual/:machineID', MachineController.getMachineManual);

    // Set up routes
    app.use('/api', apiRoutes);

}