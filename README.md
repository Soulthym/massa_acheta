# MASSA 🦗 Acheta


Acheta is a genus of crickets. It most notably contains the house cricket (Acheta domesticus).

"MASSA Acheta" is a service that will notify you about events occurring on your MASSA node and your wallet.\
Just like a little cricket!

>
>First of all let's define that this is not a public Telegram Bot, but opensource software that you can install on your own server to get a personal Bot that will be accessible only to you.
>
Public bot with limited functionality is also available here: https://t.me/massa_acheta_bot


Before we jump to a detailed description of the service, please watch the video:

[![MASSA Acheta service video](https://img.youtube.com/vi/gdvuhe2iRyY/0.jpg)](https://www.youtube.com/watch?v=gdvuhe2iRyY)



## Just one command to start:

Copy the following command and paste it into your shell prompt:
```
bash <(wget --no-cache -qO- https://raw.githubusercontent.com/Soulthym/massa_acheta/main/install.sh)
```

This command will install, configure and start your Bot automatically.


>
> !! Please check if you have a **Telegram Bot API KEY** and you do know your own **Telegram ID** before start installation
>
> How to create a new Telegam Bot and its API KEY: https://www.youtube.com/watch?v=UQrcOj63S2o
>
> You can get your own Telegram ID here: https://t.me/getmyid_bot
>


You can stop the installation process anywhere by pressing `Ctrl+C`, but before starting the installation again, run the following command to clear all changes made:
```
bash <(wget --no-cache -qO- https://raw.githubusercontent.com/Soulthym/massa_acheta/main/uninstall.sh)
```



## Update Acheta:

Acheta automatically checks for its updates, and if you receive the message “A new version of ACHETA has been released” - please update your installation.

You can do it with one command:
```
bash <(wget --no-cache -qO- https://raw.githubusercontent.com/Soulthym/massa_acheta/main/update.sh)
```

This command stops Acheta, deploys all updates ans starts Acheta again.



## Uninstall Acheta:

You can clean your system with the following command:
```
bash <(wget --no-cache -qO- https://raw.githubusercontent.com/Soulthym/massa_acheta/main/uninstall.sh)
```



## What can Acheta do:

### 👉 Explore MASSA blockchain
First of all it can observe MASSA explorer and display wallets info with command:
>
> `/view_address`
>
![view_address](https://github.com/Soulthym/massa_acheta/blob/main/img/view_address.png?raw=true)

### 👉 Watch your node
!!! You can add any number of nodes and wallets you want to your Acheta configuration.


In order to watch your node, you need to add it to the service configuration. To do this use the command:
>
> `/add_node`
>
Acheta will ask you for a node nickname (any unique value) and API URL to connect the node using MASSA public API.\
Use `http://127.0.0.1:33035/api/v2` if you installed Acheta on the same host with MASSA node, otherwise replace `127.0.0.1` with your real MASSA node IP address.

!!! Please make sure if you opened port `33035/tcp` on your MASSA node to allow the connection from Acheta!\
!!! Use `sudo ufw allow 33035/tcp` on Ubuntu hosts.

`33035/tcp` is the public API port so it's safe to open it.\
You can read more about MASSA Public API here: https://docs.massa.net/docs/build/api/jsonrpc


Once you have successfully added a node, Acheta will try to connect to it and display its current status.\
If the node is available, Acheta will start monitoring the node and will notify you if the node's status changes (`Alive -> Dead` or `Dead -> Alive`).\
Every time the status changes, you will receive warning messages about it.
Moreover, Acheta will notify you if your node becomes out of sync with the MASSA blockchain.
You also can display actual node info using command:
>
> `/view_node`
>
![view_node](https://github.com/Soulthym/massa_acheta/blob/main/img/view_node.png?raw=true)

### 👉 Watch your staking
In order to watch your wallet and staking activity, you need to add it to the service configuration. To do this use the command:
>
> `/add_wallet`
>
Acheta will ask you to select which node this wallet belongs to and will ask you to enter its address.

After succesfuly adding a wallet, Acheta will try to obtain information about it from the node and display the status of this attempt.\
If the attempt is successful, Acheta will start to watch your wallet and will send notifications about the following events:
- Decreasing the wallet balance
- Missing blocks
- Changing the number of candidate rolls
- Changing the number of active rolls

You also can display actual wallet info using command:
>
> `/view_wallet`
> 
![view_wallet](https://github.com/Soulthym/massa_acheta/blob/main/img/view_wallet.png?raw=true)

### 👉 Remind you about its status
Acheta sends heartbeat messages to your messenger every 6 hours.\
These messages contains short useful information about your nodes and wallets, including its status and balance.


### 👉 Edit configuration
To view your current configuration (added nodes and wallets) use command:
>
> `/view_config`
>

To remove added nodes or wallets use:
>
> `/delete_node`\
> `/delete_wallet`
>

To reset the whole service configuration use:
>
> `/reset`
>


### 👉 Watch full statistics of your added wallets
Acheta collects statistics on all your added wallets and can show visual charts:
>
> `/massa_info`\
> `/massa_chart`
>
![massa_chart](https://github.com/Soulthym/massa_acheta/blob/main/img/massa_chart.jpg?raw=true)
```
Cycles collected: 34
Total stakers: 1,934 (d: -6)
Total staked rolls: 363,222 (d: +1,551)
```

>
> `/view_wallet`\
> `/chart_wallet`
>
![chart_wallet](https://github.com/Soulthym/massa_acheta/blob/main/img/wallet_staking_chart.jpg?raw=true)
```
Cycles collected: 34
Current balance: 583,777.8462 MAS (d: +7,639.1536)
Number of rolls: 20,000 (d: 0)
```

![chart_wallet](https://github.com/Soulthym/massa_acheta/blob/main/img/wallet_blocks_chart.jpg?raw=true)
```
Cycles collected: 34
Operated blocks: 6,663
Estimated Blocks / Cycle: 226.0361
Fact Blocks / Cycle: 195.9706
```

### 👉 Watch deferred credits of any MASSA wallet
Acheta can check provided MASSA wallet to display all future deferred credits (full list for two years)
>
> `/view_credits`
>
![view_credits](https://github.com/Soulthym/massa_acheta/blob/main/img/view_credits.png?raw=true)

## Notes
Although you can install Acheta on the same host where your MASSA node is installed, I recommend using a different remote host for Acheta because in case the whole MASSA host fails, Acheta will be able to notify you about it.



## Thank you!
If You want to thank the author:
```
AU1qLrbaC4vWNRLvTaRFY9SBRe7oDcrVqXrjiJmuMFy4eBknBgMV
```
