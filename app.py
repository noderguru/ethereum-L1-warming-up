import asyncio

from loguru import logger

from functions.create_files import create_files
from functions.Import import Import

from data.models import Settings
from functions.initial import initial
from functions.activity import activity
from libs.py_eth_async.data import config


async def start_script():
    if not all([
        config.ETHEREUM_API_KEY,
    ]):
        logger.error(f'There are no API keys for explorers in the .env file')
    tasks = [
        asyncio.create_task(initial()),
        asyncio.create_task(activity()),
    ]
    return await asyncio.wait(tasks)


if __name__ == '__main__':
    create_files()
    main_settings = Settings()
    print('''  Select the action:
1) Import wallets from the spreadsheet to the DB;
2) Start L1 warming-up
3) Exit.''')

    try:
        action = int(input('> '))
        if action == 1:
            asyncio.run(Import.wallets())

        elif action == 2:
            asyncio.run(start_script())

    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        print()

    except ValueError as err:
        logger.error(f"Value error: {err}")

    except BaseException as e:
        logger.exception(f'\nSomething went wrong: {e}')
