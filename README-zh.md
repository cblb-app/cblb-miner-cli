# cblb-miner-cli

<!-- MarkdownTOC -->

- [使用之前的配置](#使用之前的配置)
- [初始化](#初始化)
- [转入 MATIC 到领队地址](#转入matic到领队地址)
- [开始挖矿](#开始挖矿)

<!-- /MarkdownTOC -->

cblb-miner-cli 是[cblb.app](https://cblb.app)发布的基于 Polygon 的 Cblb 签到挖矿程序，设置了`领队角色`和`矿工角色`，可以实现

- 自动生成领队钱包和矿工钱包
- 自动平衡领队钱包 MATIC 到多个矿工钱包
- 领队和矿工自动签到
- 自动归集领队和矿工钱包[CBLB](https://polygonscan.com/token/0x7a45922F95C845Ff9bE01112AfCF207968a9cA0B)代币到受益人地址

源代码开放，可以自行修改适配更多项目

<a id="使用之前的配置"></a>

## 使用之前的配置

- 修改.env 文件中的`BENEFICIARY_ADDRESS`作为接收[CBLB](https://polygonscan.com/token/0x7a45922F95C845Ff9bE01112AfCF207968a9cA0B)代币的受益人 erc20 钱包地址，默认为空（**重要**）
- 修改.env 文件中的`MINER_NUMBER`作为需要的矿工数量，默认为 50，初始化后矿工数量不支持二次修改

<a id="初始化"></a>

## 初始化

- 检查 python 版本，推荐为 3.8，推荐使用 Anaconda 配置虚拟环境
- 执行`pip install -r requirement.txt`配置环境
- 执行`python main.py`完成 miner 初始化

<a id="转入matic到领队地址"></a>

## 转入 MATIC 到领队地址

cblb-miner-cli 会自动生成对应数量的矿工钱包，对应的私钥和钱包地址保存在`wallet.json`文件中，注意该文件的安全，并不要转入大量代币！

初始化完成后，需要向`wallet.json`文件中记录的 leader 钱包地址转入 Polygon 网路下的 MATIC 代币。默认 50 个矿工推荐转入至少 3 个 MATIC，安全性考虑，不超过 100 个 MATIC。

<a id="开始挖矿"></a>

## 开始挖矿

确认转入 MATIC 到领队地址后，执行下面的命令开始挖矿

```
python main.py
```

DYOR!
