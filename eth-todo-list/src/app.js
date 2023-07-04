App = {
    loading: false,
    contracts: {},

    load: async () => {
        await App.loadWeb3()
        await Promise.all([App.loadAccount(), App.loadContract()])
        await App.render()
    },

    // https://medium.com/metamask/https-medium-com-metamask-breaking-change-injecting-web3-7722797916a8
    loadWeb3: async () => {
        if (window.ethereum) {
              window.web3 = new Web3(ethereum)
              try {
                // Request account access if needed
                await ethereum.enable()
                // Accounts now exposed
                // web3.eth.sendTransaction({/* ... */})
              } catch (error) {
                window.alert("User denied account access...")
              }
        }
        // Legacy dapp browsers...
        else if (window.web3) {
            window.web3 = new Web3(web3.currentProvider);
            // Accounts always exposed
            // web3.eth.sendTransaction({/* ... */});
        }
        // Non-dapp browsers...
        else {
            console.log('Non-Ethereum browser detected. You should consider trying MetaMask!');
        }
    },

    loadAccount: async () => {
        let accounts = await web3.eth.getAccounts()
        App.account = accounts[0]
        console.log(App.account)
    },

    loadContract: async () => {
        const todoList = await $.getJSON("TodoList.json")
        // contract instance
        App.contracts.todoList = TruffleContract(todoList)
        App.contracts.todoList.setProvider(web3.currentProvider)

        App.todoList = await App.contracts.todoList.deployed()
    },

    renderTasks: async () => {
        const nonCompletedTaskList = $('#taskList')
        const completedTaskList = $('#completedTaskList')
        const taskTemplate = $(".taskTemplate")
        const TaskCount = await App.todoList.taskCount()

        for (let i = 0; i < TaskCount; i++) {
            let newTaskTemplate = taskTemplate.clone()
            let task = await App.todoList.tasks(i)
            let taskId = task.id.toNumber()
            let content = task.content
            let done = task.done

            newTaskTemplate.find(".content").html(content)
            newTaskTemplate.find("input")
                .prop("name", taskId)
                .prop("checked", done)

            if (done) {
                completedTaskList.append(newTaskTemplate)
            } else {
                nonCompletedTaskList.append(newTaskTemplate)
            }
            newTaskTemplate.show()
        }

    },

    render: async () => {
        App.setLoading(true)

        $('#account').html(App.account)
        await App.renderTasks()

        App.setLoading(false)
    },

    setLoading: (isLoading) => {
        const loader = $('#loader')
        const content = $('#content')
        if (isLoading) {
            loader.show()
            content.hide()
        } else {
            loader.hide()
            content.show()
        }
    }
}


$(() => {
    $(window).load(() => {
        App.load()
    })
})

