const todoListContract = artifacts.require("TodoList");

contract("TodoList", (accounts) => {
    it("contract should deployed", async () => {
        const c = await todoListContract.deployed()
        assert.notEqual(c.address, 0x0)
        assert.notEqual(c.address, '')
        assert.notEqual(c.address, null)
        assert.notEqual(c.address, undefined)
    })

    it("should have one task", async () => {
        const c = await todoListContract.deployed()
        const taskCount = await c.taskCount()
        assert.strictEqual(taskCount.toNumber(), 1)
    })

    it("can add tasks", async () => {
        let content = "hello world"
        const c = await todoListContract.deployed()
        await c.createTask(content)

        const taskCount = await c.taskCount()
        const task = await c.tasks(1)

        assert.strictEqual(taskCount.toNumber(), 2)
        assert.strictEqual(task.content, content)
        assert.strictEqual(task.done, false)
    })
})