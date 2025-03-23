import asyncio

from loguru import logger

from libs.py_eth_async.client import Client
from libs.py_eth_async.data.models import Networks

from utils.db_api.models import Wallet
from data.models import Settings


async def check_gas(proxy: str | None = None):
    settings = Settings()
    client = Client(private_key='', network=Networks.Ethereum, proxy=proxy)
    gas_price = await client.transactions.gas_price()

    while gas_price.Wei > settings.maximum_gas_price.Wei:
        logger.debug(f'Gas price is too hight '
                     f'({gas_price.GWei} > {settings.maximum_gas_price.GWei})')
        await asyncio.sleep(settings.time_between_gas_checks)
        gas_price = await client.transactions.gas_price()
