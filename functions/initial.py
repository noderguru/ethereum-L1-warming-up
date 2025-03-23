import random
import asyncio
from datetime import datetime

from loguru import logger
from sqlalchemy import select, func

from libs.py_eth_async.client import Client
from libs.py_eth_async.data.models import Networks

from data.models import Settings
from data.config import DELAY_IN_CASE_OF_ERROR
from utils.db_api.wallet_api import db
from utils.db_api.models import Wallet
from tasks.controller import Controller
from functions.select_random_action import select_random_action
from utils.update_expired import update_expired, update_next_action_time
from utils.gas_checker import check_gas


async def initial():
    settings = Settings()
    delay = 10

    update_expired(initial=True)
    await asyncio.sleep(5)

    while True:
        try:
            now = datetime.now()

            wallet: Wallet = db.one(
                Wallet, Wallet.initial_completed.is_(False) & (Wallet.next_initial_action_time <= now)
            )

            if not wallet:
                await asyncio.sleep(delay)
                continue

            await check_gas(proxy=wallet.proxy)

            client = Client(private_key=wallet.private_key, network=Networks.Ethereum, proxy=wallet.proxy)
            controller = Controller(client=client)

            action = await select_random_action(controller=controller, wallet=wallet, initial=True)

            if not action:
                logger.error(f'{wallet.address} | select_random_action | can not choose the action')
                update_next_action_time(private_key=wallet.private_key, seconds=DELAY_IN_CASE_OF_ERROR, initial=True)
                continue

            elif action == 'Processed':
                wallet.initial_completed = True
                db.commit()

                update_next_action_time(
                    private_key=wallet.private_key,
                    seconds=random.randint(settings.activity_actions_delay.from_, settings.activity_actions_delay.to_),
                    initial=False
                )
                logger.success(
                    f'{wallet.address}: initial actions completed!'
                )
                continue

            elif action == 'Insufficient balance':
                logger.error(f'{wallet.address}: Insufficient balance')
                update_next_action_time(private_key=wallet.private_key, seconds=DELAY_IN_CASE_OF_ERROR, initial=True)
                continue

            status = await action()

            if 'Failed' not in status:
                update_next_action_time(
                    private_key=wallet.private_key,
                    seconds=random.randint(settings.initial_actions_delay.from_, settings.initial_actions_delay.to_),
                    initial=True
                )

                logger.success(f'{wallet.address}: {status}')

                stmt = select(func.min(Wallet.next_initial_action_time)).where(Wallet.initial_completed.is_(False))
                next_action_time = db.one(stmt=stmt)

                logger.info(f'The next closest initial action will be performed at {next_action_time}')

                await asyncio.sleep(delay)

            else:
                update_next_action_time(private_key=wallet.private_key, seconds=DELAY_IN_CASE_OF_ERROR, initial=True)
                logger.error(f'{wallet.address}: {status}')

        except BaseException as e:
            logger.exception(f'Something went wrong: {e}')

        finally:
            await asyncio.sleep(delay)
