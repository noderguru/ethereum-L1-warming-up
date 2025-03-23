import csv
import os

from libs.pretty_utils.miscellaneous.files import touch, write_json, read_json
from libs.pretty_utils.type_functions.dicts import update_dict

from data import config
from data.models import WalletCSV


def create_files():
    touch(path=config.FILES_DIR)
    touch(path=config.LOG_FILE, file=True)
    touch(path=config.ERRORS_FILE, file=True)

    if not os.path.exists(config.IMPORT_FILE):
        with open(config.IMPORT_FILE, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(WalletCSV.header)

    try:
        current_settings: dict | None = read_json(path=config.SETTINGS_FILE)
    except Exception:
        current_settings = {}

    settings = {
        'maximum_gas_price': 20,
        'time_between_gas_checks': 60,

        'okx': {
            'required_minimum_balance': 0.001,
            'withdraw_amount': {'from': 0.006, 'to': 0.007},
            'delay_between_withdrawals': {'from': 1200, 'to': 1500},
            'credentials': {
                'api_key': '',
                'secret_key': '',
                'passphrase': '',
            }
        },

        'minimal_balance': 0.00375,

        'number_of_telepathy': {'from': 1, 'to': 1},
        'number_of_wrap_unwrap_eth': {'from': 1, 'to': 2},
        'number_of_swaps': {'from': 1, 'to': 2},
        'number_of_bungee': {'from': 1, 'to': 2},
        'number_of_blur': {'from': 1, 'to': 2},
        'number_of_l2marathon_nft': {'from': 0, 'to': 1},
        'number_of_merkly_nft': {'from': 0, 'to': 1},

        'initial_actions_delay': {'from': 3600, 'to': 28800},
        'activity_actions_delay': {'from': 3600, 'to': 28800},

        'eth_amount_for_swap': {'from': 0.0001, 'to': 0.0002},
    }
    write_json(path=config.SETTINGS_FILE, obj=update_dict(modifiable=current_settings, template=settings), indent=2)


create_files()
