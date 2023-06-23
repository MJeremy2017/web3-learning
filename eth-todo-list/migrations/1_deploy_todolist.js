const ToDoListContract = artifacts.require("TodoList");

module.exports = function(deployer) {
  deployer.deploy(ToDoListContract)
};