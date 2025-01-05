import bip32utils
import os
from time import sleep
from pathlib import Path

import requests
from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.providers import HTTPProvider
from mnemonic import Mnemonic
from loguru import logger

script_dir = Path(__file__).parent.resolve()
log_format = "<green>{time:YYYY-MM-DD HH:mm:ss zz}</green> | <level>{level: <8}</level> | <yellow>Line {line: >4} ({file}):</yellow> <b>{message}</b>"
logger.add(script_dir / "script.log", level="INFO", format=log_format, colorize=False, backtrace=True, diagnose=True)

CONTROLLED_ADDR = os.environ["CONTROLLED_ADDR"]
ADMIN_ADDR = os.environ["ADMIN_ADDR"]
TRANSIT_ADDR = os.environ["TRANSIT_ADDR"]

TRON_GRID_API_KEY = os.environ["TRON_GRID_API_KEY"]
ADMIN_MNEMONIC = os.environ["ADMIN_MNEMONIC"] 

TRX_RESERVED_FEE = 1
TRX_SEND_THRESHOLD = 25
LOOP_TIMEOUT = 60
RAISED_LIMIT = int(os.getenv("RAISED_LIMIT", 100000))

# For alerting via telegram bot
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
TG_ALERT_SEND_TIMEOUT = 15

client = Tron(HTTPProvider(api_key=TRON_GRID_API_KEY))

mnemo = Mnemonic("english")
seed = mnemo.to_seed(ADMIN_MNEMONIC)
admin_master_key = bip32utils.BIP32Key.fromEntropy(seed)
admin_child_key = admin_master_key.ChildKey(44 + bip32utils.BIP32_HARDEN) \
    .ChildKey(195 + bip32utils.BIP32_HARDEN) \
    .ChildKey(0 + bip32utils.BIP32_HARDEN) \
    .ChildKey(0) \
    .ChildKey(0)
admin_private_key = PrivateKey(admin_child_key.PrivateKey())


def get_trx_balance(trx_client: Tron, trx_address: str) -> float: 
    balance = float(trx_client.get_account_balance(trx_address))
    return balance


def send_trx(
    trx_client: Tron,
    private_key: PrivateKey,
    from_addr: str = CONTROLLED_ADDR,
    to_addr: str = TRANSIT_ADDR,
    amount: float | None = None,
):
    normalize_amount = int((amount - TRX_RESERVED_FEE) * 1e6)
    txn = (
        trx_client.trx.transfer(from_addr, to_addr, 10)
        .build()
        .inspect()
        .sign(private_key)
        .broadcast()
    )
    msg = f"Sent {normalize_amount / 1_000_000} TRX, transaction ID: {txn.txid}"
    logger.info(msg)
    send_telegram_message(msg)


def send_telegram_message(
    message: str,
    tg_bot_token: str | None = TG_BOT_TOKEN,
    tg_chat_id: str | None = TG_CHAT_ID,
) -> None:
    if not (tg_bot_token and tg_chat_id):
        logger.warning("TG_BOT_TOKEN or TG_CHAT_ID are not set!")
        return
    url = f"https://api.telegram.org/bot{tg_bot_token}/sendMessage"
    params = {
        "chat_id": tg_chat_id,
        "text": message
    }
    response = requests.post(url, params=params, timeout=TG_ALERT_SEND_TIMEOUT)
    response.raise_for_status()


def main() -> None:
    uninspected_raise = 0
    loop_enter = False
    send_telegram_message("Bot started.")
    while True:
        try:
            trx_balance = get_trx_balance(client, CONTROLLED_ADDR)
            logger.info(f"Current balance: {trx_balance} TRX")
            if trx_balance > TRX_SEND_THRESHOLD:
                send_trx(trx_client=client, private_key=admin_private_key, amount=trx_balance)
        except Exception:
            logger.warning(f"Uninspected raise #{uninspected_raise}")
            uninspected_raise += 1
            loop_enter = False
        finally:
            if uninspected_raise % 100 == 0 and not loop_enter:
                loop_enter = True
                send_telegram_message(f"Bot is alive. uninspected_raise: {uninspected_raise}")
            if uninspected_raise > RAISED_LIMIT:
                logger.exception("Uninspected loop error limit reached!")
                send_telegram_message(f"Bot is dead. Uninspected loop error limit reached!")
                raise
            else:
                sleep(LOOP_TIMEOUT)


if __name__ == "__main__":
    main()
