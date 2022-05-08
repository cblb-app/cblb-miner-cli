# cblb-miner-cli

<!-- MarkdownTOC -->

- [Use previous configuration](#use-previous-configuration)
- [Initialize](#initialize)
- [Transfer MATIC to the tour leader's address](#transfer-matic-to-the-tour-leaders-address)
- [Start mining](#start-mining)

<!-- /MarkdownTOC -->

cblb-miner-cli is a Polygon-based Cblb check-in mining program released by [cblb.app](https://cblb.app). It has set the `leader role` and `miner role`, which can be realized

- Automatically generate leader wallet and miners' wallets
- Automatically balance leader wallet MATIC to multiple miners' wallets
- leader and miners automatically do cblb-check-in acquire CBLB token
- Automatic collection of [CBLB](https://polygonscan.com/token/0x7a45922F95C845Ff9bE01112AfCF207968a9cA0B) tokens from leader and miner wallets to beneficiary addresses

Open source code, you can modify and adapt to more projects

<a id="use-previous-configuration"></a>

## Use previous configuration

- Modify `BENEFICIARY_ADDRESS` in .env file as beneficiary erc20 wallet address for receiving CBLB tokens, default is empty (**important**)
- Modify `MINER_NUMBER` in the .env file as the required number of miners, the default is 100. The number of miners after initialization does not support secondary modification

<a id="initialize"></a>

## Initialize

- Check the python version, it is recommended to be `3.8`, it is recommended to use Anaconda to configure the virtual environment
- Execute `pip install -r requirement.txt` to configure the environment
- Execute `python main.py` to complete miner initialization

<a id="transfer-matic-to-the-tour-leaders-address"></a>

## Transfer MATIC to the tour leader's address

cblb-miner-cli will automatically generate the corresponding number of miner wallets and save PRIVATE KEY and WALLET ADDRESS within the `wallet.json` file, keep this file safe and DO NOT transfer large amount token.

After the initialization is completed, you need to transfer the MATIC tokens under the Polygon network to the leader wallet address recorded in the wallet.json file. By default, 50 miners are recommended to transfer at least 3 MATICs, and for security reasons, no more than 100 MATICs.

<a id="start-mining"></a>

## Start mining

After confirming the transfer to MATIC to the leader's address, execute the following command to start mining [CBLB](https://polygonscan.com/token/0x7a45922F95C845Ff9bE01112AfCF207968a9cA0B)

```
python main.py
```

Have fun! DYOR!
