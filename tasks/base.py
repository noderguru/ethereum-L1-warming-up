import aiohttp
import asyncio

from libs.pretty_utils.type_functions.floats import randfloat
from libs.py_eth_async.client import Client
from libs.py_eth_async.data.models import Ether, Wei, Unit, TokenAmount

from data.config import logger
from data.models import Settings


class Base:
    def __init__(self, client: Client):
        self.client = client

    @staticmethod
    def get_random_amount(
            from_: float | int,
            to_: float | int,
            step: float = 0.0000001
    ) -> Unit:
        if to_ < from_:
            raise Exception(f'parameter "to_" ({to_}) less than parameter "from_" ({from_})')

        amount = randfloat(
            from_=from_,
            to_=to_,
            step=step
        )

        if isinstance(from_, float) or isinstance(to_, float):
            return Ether(amount)
        return Wei(amount)

    @staticmethod
    def get_random_eth_amount_by_balance(
            balance: Unit | TokenAmount,
            from_: float | int | None = None,
            to_: float | int | None = None,
            step: float = 0.0000001
    ) -> Ether:
        settings = Settings()

        if not from_:
            from_ = settings.eth_amount_for_swap.from_
        if not to_:
            to_ = settings.eth_amount_for_swap.to_

        if float(balance.Ether) - settings.minimal_balance < to_:
            to_ = float(balance.Ether) - settings.minimal_balance

        if to_ < from_:
            raise Exception(f'parameter "to_" ({to_}) less than parameter "from_" ({from_})')

        return Ether(randfloat(
            from_=from_,
            to_=to_,
            step=step
        ))

    @staticmethod
    async def get_token_price(token_symbol='ETH', second_token: str = 'USDT') -> float | None:
        token_symbol, second_token = token_symbol.upper(), second_token.upper()

        if token_symbol.upper() in ('USDC', 'USDT', 'DAI', 'CEBUSD', 'BUSD'):
            return 1
        if token_symbol == 'WETH':
            token_symbol = 'ETH'
        if token_symbol == 'WBTC':
            token_symbol = 'BTC'

        for _ in range(5):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                            f'https://api.binance.com/api/v3/depth?limit=1&symbol={token_symbol}{second_token}') as r:
                        if r.status != 200:
                            return None
                        result_dict = await r.json()
                        if 'asks' not in result_dict:
                            return None
                        return float(result_dict['asks'][0][0])
            except Exception:
                await asyncio.sleep(5)
        raise ValueError(f'Can not get {token_symbol + second_token} price from Binance')
