# 🚀 L1-Warming-Up | Ethereum Wallet Activity Booster

Скрипт для прогрева кошельков транзакциями в основной сети Ethereum L1. Также доступен вывод средств с биржи OKX.

Вся информация/действия/маршрут кошельков записываются в базу данных ```wallets.db```, которую можно после импорта редактировать вручную сторонней программой DB Browser for SQLite

![GitHub](https://img.shields.io/badge/python-3.9+-blue?logo=python)
![License](https://img.shields.io/badge/license-MIT-green)

Транзакции:

- 🌉 Отправка интерчейн сообщений через telepathy (Succinct) в рандомные сети (https://docs.telepathy.xyz/build-with-telepathy/interchain-messaging/example-cross-chain-counter)
- 🔄 wrap_unwrap_eth
- 💱 свопы на стэйблкоины ShibaSwap
- ⛽ Рефуел на Bungee в рандомные сети
- 🎨 Депозит/вывод ETH на NFT макретплэйс Blur
- 🏅 Минт NFT на l2marathon
- 🖼️ Минт NFT на merkly
- ⚙️  в настройках можно выставить максимальный газ при котором будут производится транзакции maximum_gas_price

  -----

Подготовка к запуску:
```bash
git clone https://github.com/noderguru/ethereum-L1-warming-up.git && cd ethereum-L1-warming-up
```
```bash
python3 -m venv venv
source venv/bin/activate
```
```bash
pip install -r requirements.txt
```
```bash
cp .env_example .env
```
```bash
nano .env
```
сюда вставляем ссылку на RPC Ethereum mainnet https://dashboard.alchemy.com и API ключ с https://etherscan.io/apidashboard
```bash
python3 app.py
```

🛠 Автоматически создаваемые файлы при первом запуске ```app.py```
При запуске скрипта вызывается функция create_files(), которая создаёт необходимые файлы и структуру:

📁 files/ — основная рабочая папка, если она ещё не существует

📄 files/import.csv — шаблон для импорта кошельков (вставляем как указано внутри файла в примере без пробелов)

📄 files/errors.log — лог ошибок

📄 files/log.log — основной лог действий скрипта

📄 files/settings.json — настройки вывода с биржи (если необходимо), количество свопов, минтов, задержки, максимальный газ и пр.

После того как запустили скрипт, необходимо выйти из него через меню и заполнить файлы ```import.csv``` и ```settings.json```

формат прокси в ```import.csv``` http://{username}:{password}@{host}:{port}

затем заново запускаем и выбираем 1) Import wallets from the spreadsheet to the DB создаейтся файл ```wallets.db``` тут /l1-warming-up-main/files/

Теперь мы можем запустить скрипт снова и выбрать 2) Start L1 warming-up

----

# 🚀 L1-Warming-Up | Eng

A script for warming up wallets with transactions on the Ethereum L1 mainnet. It also supports fund withdrawals from the OKX exchange.

All information, actions, and wallet routes are recorded in the database ```wallets.db```, which can be manually edited later using a third-party program like DB Browser for SQLite.

Transactions:
- 🌉 Sending interchain messages via telepathy (Succinct) to random networks (Example)
- 🔄 wrap_unwrap_eth
- 💱 Swaps for stablecoins on ShibaSwap
- ⛽ Refuel on Bungee to random networks
- 🎨 Deposit/withdraw ETH on the NFT marketplace Blur
- 🏅 Mint NFT on l2marathon
- 🖼️ Mint NFT on Merkly
- ⚙️ In the settings, you can set the maximum gas price for transactions (maximum_gas_price)

----

Getting Started:
```bash
git clone https://github.com/noderguru/ethereum-L1-warming-up.git && cd ethereum-L1-warming-up
```
```bash
python3 -m venv venv
source venv/bin/activate
```
```bash
pip install -r requirements.txt
```
```bash
cp .env_example .env
```
```bash
nano .env
```
Paste the Ethereum mainnet RPC link (from Alchemy) and the API key from Etherscan into the file.

```bash
python3 app.py
```
🛠 Files automatically generated on the first run of app.py

When the script is executed, the create_files() function is called, which creates the necessary files and structure:

📁 files/ — the main working folder, if it doesn't already exist

📄 files/import.csv — a template for importing wallets (insert data as indicated in the example inside the file, without spaces)

📄 files/errors.log — error log

📄 files/log.log — main script activity log

📄 files/settings.json — settings for withdrawals from the exchange (if needed), number of swaps, mints, delays, maximum gas, etc.

After running the script, exit it via the menu and fill in the files ```import.csv``` and ```settings.json```.

The proxy format in import.csv is: http://{username}:{password}@{host}:{port}

Then, run the script again and choose 1) Import wallets from the spreadsheet to the DB. The file ```wallets.db will``` be created in the /l1-warming-up-main/files/ directory.

Now you can run the script once more and choose 2) Start L1 warming-up.
