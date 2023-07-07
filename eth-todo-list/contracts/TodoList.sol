pragma solidity ^0.8.20;

contract TodoList {
    uint public taskCount = 0;
    mapping(uint => Task) public tasks;

    struct Task {
        uint id;
        string content;
        bool done;
    }

    event TaskCreated(uint id, string content, bool done);

    constructor() {
        createTask("Add something.");
    }

    function createTask(string memory _content) public {
        tasks[taskCount] = Task(taskCount, _content, false);
        emit TaskCreated(taskCount, _content, false);

        taskCount++;
    }

    function toggleCompleted(uint id) public {
        Task memory _task = tasks[id];
        _task.done = !_task.done;
        tasks[id] = _task;
    }

}