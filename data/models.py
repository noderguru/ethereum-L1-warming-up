from dataclasses import dataclass

from libs.pretty_utils.miscellaneous.files import read_json
from libs.pretty_utils.type_functions.classes import AutoRepr, Singleton
from libs.py_eth_async.data.models import GWei, RawContract, DefaultABIs
from libs.py_okx_async.models import OKXCredentials

from data.config import SETTINGS_FILE, ABIS_DIR


@dataclass
class FromTo:
    from_: int | float
    to_: int | float


@dataclass
class WalletCSV:
    header = ['private_key', 'proxy', 'name']

    def __init__(self, private_key: str, proxy: str = '', name: str = ''):
        self.private_key = private_key
        self.proxy = proxy
        self.name = name


class BaseContract(RawContract):
    def __init__(self, title, address, abi):
        super().__init__(address, abi)
        self.title = title


class OkxModel:
    required_minimum_balance: float
    withdraw_amount: FromTo
    delay_between_withdrawals: FromTo
    credentials: OKXCredentials


class Settings(Singleton, AutoRepr):
    def __init__(self):
        json_data = read_json(path=SETTINGS_FILE)

        self.maximum_gas_price: GWei = GWei(json_data['maximum_gas_price'])
        self.time_between_gas_checks: int = json_data['time_between_gas_checks']

        self.okx = OkxModel()
        self.okx.required_minimum_balance = json_data['okx']['required_minimum_balance']
        self.okx.withdraw_amount = FromTo(
            from_=json_data['okx']['withdraw_amount']['from'],
            to_=json_data['okx']['withdraw_amount']['to'],
        )
        self.okx.delay_between_withdrawals = FromTo(
            from_=json_data['okx']['delay_between_withdrawals']['from'],
            to_=json_data['okx']['delay_between_withdrawals']['to'],
        )
        self.okx.credentials = OKXCredentials(
            api_key=json_data['okx']['credentials']['api_key'],
            secret_key=json_data['okx']['credentials']['secret_key'],
            passphrase=json_data['okx']['credentials']['passphrase']
        )

        self.minimal_balance: float = json_data['minimal_balance']

        self.number_of_telepathy: FromTo = FromTo(
            from_=json_data['number_of_telepathy']['from'], to_=json_data['number_of_telepathy']['to']
        )
        self.number_of_wrap_unwrap_eth: FromTo = FromTo(
            from_=json_data['number_of_wrap_unwrap_eth']['from'], to_=json_data['number_of_wrap_unwrap_eth']['to']
        )
        self.number_of_swaps: FromTo = FromTo(
            from_=json_data['number_of_swaps']['from'], to_=json_data['number_of_swaps']['to']
        )
        self.number_of_bungee: FromTo = FromTo(
            from_=json_data['number_of_bungee']['from'], to_=json_data['number_of_bungee']['to']
        )
        self.number_of_blur: FromTo = FromTo(
            from_=json_data['number_of_blur']['from'], to_=json_data['number_of_blur']['to']
        )
        self.number_of_l2marathon_nft: FromTo = FromTo(
            from_=json_data['number_of_l2marathon_nft']['from'], to_=json_data['number_of_l2marathon_nft']['to']
        )
        self.number_of_merkly_nft: FromTo = FromTo(
            from_=json_data['number_of_merkly_nft']['from'], to_=json_data['number_of_merkly_nft']['to']
        )

        self.initial_actions_delay: FromTo = FromTo(
            from_=json_data['initial_actions_delay']['from'], to_=json_data['initial_actions_delay']['to']
        )
        self.activity_actions_delay: FromTo = FromTo(
            from_=json_data['activity_actions_delay']['from'], to_=json_data['activity_actions_delay']['to']
        )

        self.eth_amount_for_swap: FromTo = FromTo(
            from_=json_data['eth_amount_for_swap']['from'], to_=json_data['eth_amount_for_swap']['to']
        )


class Contracts(Singleton):
    # Ethereum
    WETH = BaseContract(
        title='WETH',
        address='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        abi=read_json(path=(ABIS_DIR, 'weth.json'))
    )
    USDC = BaseContract(
        title='USDC',
        address='0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        abi=DefaultABIs.Token
    )
    USDT = BaseContract(
        title='USDT',
        address='0xdAC17F958D2ee523a2206206994597C13D831ec7',
        abi=DefaultABIs.Token
    )
    DAI = BaseContract(
        title='DAI',
        address='0x6B175474E89094C44Da98b954EedeAC495271d0F',
        abi=DefaultABIs.Token
    )
    WBTC = BaseContract(
        title='WBTC',
        address='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
        abi=DefaultABIs.Token
    )

    TELEPATHY = BaseContract(
        title='TELEPATHY',
        address='0xa3b31028893c20bEAA882d1508Fe423acA4A70e5',
        abi=read_json(path=(ABIS_DIR, 'telepathy.json'))
    )

    BUNGEE = BaseContract(
        title='BUNGEE',
        address='0xb584D4bE1A5470CA1a8778E9B86c81e165204599',
        abi=read_json(path=(ABIS_DIR, 'bungee.json'))
    )

    BLUR = BaseContract(
        title='BLUR',
        address='0x0000000000A39bb272e79075ade125fd351887Ac',
        abi=read_json(path=(ABIS_DIR, 'blur.json'))
    )

    SHIBASWAP = BaseContract(
        title='SHIBASWAP',
        address='0x03f7724180AA6b939894B5Ca4314783B0b36b329',
        abi=read_json(path=(ABIS_DIR, 'shibaswap.json'))
    )

    MERKLY = BaseContract(
        title='MERKLY',
        address='0x6f6aE8851a460406bBB3c929a415d2Df9305AcD5',
        abi=read_json(path=(ABIS_DIR, 'merkly.json'))
    )

    L2MARATHON = BaseContract(
        title='L2MARATHON',
        address='0x2FF6a890249bcc6ab071c17a66Db4C327154604C',
        abi=read_json(path=(ABIS_DIR, 'l2marathon.json'))
    )
