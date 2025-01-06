# trx-transaction-bot

Simple bot that allows withdraw TRX from a multisig account to any other address automatically and flexible.

# Install

### Prepare venv

```
# create venv
python3 -m venv trx
# enable venv
source trx/bin/activate
# install requirements in venv
python3 -m pip install -r requirements.txt
```

### Set .env file with your values

Your can setup envs in `example.env` and copy it to `.env`

```
# Address with multisig
CONTROLLED_ADDR=
# Address has permissions for CONTROLLED_ADDR
ADMIN_ADDR=
# Address for withdraw CONTROLLED_ADDR
TRANSIT_ADDR=

# API key from https://www.trongrid.io/ simple registred and create free API key
TRON_GRID_API_KEY=
# ADMIN_ADDR seed pharase with control of CONTROLLED_ADDR
ADMIN_MNEMONIC=

# Optional. Your Telegram chatID for alerting via bot (ChatID can get via @getmyid_bot)
TG_CHAT_ID=
# Optional. Telegram bot token for alerting, create via @BotFather
TG_BOT_TOKEN=
```

# [Optional] Create systemd service for linux

If you want automatic bot start after rebooting.

1. Edit `trx_bot.service` and change `ExecStart` for your absolute path to bot script
2. Change or setup envs in `trx_bot_start.sh`: `WOKING_DIRECTORY` and `VENV_PATH`
2. Copy .service file to systemd dir: `sudo cp trx_bot.service /etc/systemd/system/`
3. Enable our service: `sudo systemctl enable trx_bot`
4. May take restart systemctl daemon: `sudo systemctl daemon-reload`

Check status and logs: `sudo systemctl status trx_bot`

Disable service: `sudo systemctl disable trx_bot`

# Run bot
1. Change or setup envs in `trx_bot_start.sh`: `WOKING_DIRECTORY` and `VENV_PATH`
2. Change script mod for executing: `sudo chmod +x ./trx_bot_start.sh`
3. Start bot: `./trx_bot_start.sh`
