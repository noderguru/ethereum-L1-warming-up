from libs.py_eth_async.client import Client

from data.models import Contracts
from tasks.base import Base
from tasks.eth_wrapper import ETHWrapper
from tasks.telepathy import Telepathy
from tasks.bungee import BungeeController
from tasks.blur import Blur
from tasks.shibaswap import Shibaswap
from tasks.l2marathon_mint import L2Marathon
from tasks.merkly_mint import Merkly


class Controller(Base):
    def __init__(self, client: Client):
        super().__init__(client)

        self.base = Base(client=client)
        self.eth_wrapper = ETHWrapper(client=client)
        self.telepathy = Telepathy(client=client)
        self.bungee = BungeeController(client=client)
        self.blur = Blur(client=client)
        self.shibaswap = Shibaswap(client=client)
        self.l2marathon = L2Marathon(client=client)
        self.merkly = Merkly(client=client)

    async def count_wrap_unwrap_eth(self, coin_txs: list[dict] | None):
        result_count = 0

        # ----------------------- wrap eth -----------------------
        result_count += len(await self.client.transactions.find_txs(
            contract=Contracts.WETH.address,
            function_name='deposit',
            coin_txs=coin_txs
        ))

        # ----------------------- unwrap eth -----------------------
        result_count += len(await self.client.transactions.find_txs(
            contract=Contracts.WETH.address,
            function_name='withdraw',
            coin_txs=coin_txs
        ))

        return result_count

    async def count_swaps(self, coin_txs: list[dict] | None):
        result_count = 0

        # ----------------------- coin -> token ShibaSwap -----------------------
        result_count += len(await self.client.transactions.find_txs(
            contract=Contracts.SHIBASWAP.address,
            function_name='swapExactETHForTokens',
            coin_txs=coin_txs
        ))

        # ----------------------- token -> coin ShibaSwap -----------------------
        result_count += len(await self.client.transactions.find_txs(
            contract=Contracts.SHIBASWAP.address,
            function_name='swapExactTokensForETH',
            coin_txs=coin_txs
        ))

        return result_count

    async def count_telepathy(self, coin_txs: list[dict] | None):
        result_count = 0

        # ----------------------- telepathy -----------------------
        result_count += len(await self.client.transactions.find_txs(
            contract=Contracts.TELEPATHY.address,
            function_name='sendMail',
            coin_txs=coin_txs
        ))

        return result_count

    async def count_bungee(self, coin_txs: list[dict] | None):
        result_count = 0

        # ----------------------- bungee -----------------------
        result_count += len(await self.client.transactions.find_txs(
            contract=Contracts.BUNGEE.address,
            function_name='depositNativeToken',
            coin_txs=coin_txs
        ))

        return result_count

    async def count_blur_dep_wd(self, coin_txs: list[dict] | None = None):
        result_count = 0

        # ----------------------- blur -----------------------
        result_count += len(await self.client.transactions.find_txs(
            contract=Contracts.BLUR.address,
            function_name='deposit',
            coin_txs=coin_txs
        ))

        # ----------------------- unwrap eth -----------------------
        result_count += len(await self.client.transactions.find_txs(
            contract=Contracts.BLUR.address,
            function_name='withdraw',
            coin_txs=coin_txs
        ))

        return result_count
