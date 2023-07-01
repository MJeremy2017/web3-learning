App = {
    loading: false,
    contracts: {},

    load: async () => {
        await App.loadWeb3()
        await App.loadAccount()
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
    }
}


$(() => {
    $(window).load(() => {
        App.load()
    })
})

