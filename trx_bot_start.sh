#!/usr/bin/env bash
WOKING_DIRECTORY=${WOKING_DIRECTORY:-"/home/pi/projects/trx-transaction-bot"}
VENV_PATH=${VENV_PATH:-"/home/pi/projects/venv/trx/bin/activate"}
source $VENV_PATH && export $(cat $WOKING_DIRECTORY/.env | xargs) && python3 $WOKING_DIRECTORY/trx_bot.py
