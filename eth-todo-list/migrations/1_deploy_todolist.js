var toDoListContract = artifacts.require("TodoList");

module.exports = function(deployer) {
  deployer.deploy(toDoListContract)
};