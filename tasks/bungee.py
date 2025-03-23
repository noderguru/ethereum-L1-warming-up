from libs.py_eth_async.data.models import Ether, Wei
from libs.pretty_utils.type_functions.floats import randfloat
from libs.py_eth_async.transactions import Tx
from libs.py_eth_async.client import Client
from libs.py_bungee_async import exceptions
from libs.py_bungee_async.functions import Bungee
from libs.py_bungee_async.models import SupportedNetworks, SupportedNetwork

from tasks.base import Base
from data.models import Settings


class BungeeController(Base):
    def __init__(self, client: Client):
        super().__init__(client=client)
        self.bungee = Bungee(client=client)

    async def get_random_amount(self, dest_network=SupportedNetworks.Arbitrum) -> Ether | None:
        settings = Settings()

        min_amount, max_amount = await self.bungee.get_min_max_amount(dest_network=dest_network)
        min_amount, max_amount = Wei(min_amount), Wei(max_amount)

        if settings.eth_amount_for_swap.to_ < float(min_amount.Ether):
            return None
        if settings.eth_amount_for_swap.to_ < float(max_amount.Ether):
            max_amount = Ether(settings.eth_amount_for_swap.to_)
        if settings.eth_amount_for_swap.from_ > float(min_amount.Ether):
            min_amount = Ether(settings.eth_amount_for_swap.from_)

        amount = Ether(randfloat(
            from_=float(min_amount.Ether),
            to_=float(max_amount.Ether),
            step=0.000001
        ))

        return amount

    async def refuel(self, amount: Ether, dest_network: SupportedNetwork) -> Tx | None:
        tx = await self.bungee.refuel(dest_network=dest_network, amount=amount)
        receipt = await tx.wait_for_receipt(client=self.client)
        if receipt:
            return tx

    async def _refuel(self, dest_network: SupportedNetwork):
        failed_text = f'Failed refuel to {dest_network.network.name}'

        try:
            amount = await self.get_random_amount(dest_network=dest_network)
            if not amount:
                return f'{failed_text}: to low "eth_amount_for_swap.to_" parameter'

            if tx := await self.refuel(amount=amount, dest_network=dest_network):
                return f'ETH was refuel to {dest_network.network.name}: {tx.hash.hex()}'
            return failed_text

        except exceptions.InsufficientBalance:
            return f'{failed_text}: Insufficient balance'

        except Exception as e:
            return f'{failed_text}: {str(e)}'

    async def refuel_to_gnosis(self):
        return await self._refuel(dest_network=SupportedNetworks.Gnosis)

    async def refuel_to_polygon(self):
        return await self._refuel(dest_network=SupportedNetworks.Polygon)

    async def refuel_to_zksync(self):
        return await self._refuel(dest_network=SupportedNetworks.zkSync)

    async def refuel_to_optimism(self):
        return await self._refuel(dest_network=SupportedNetworks.Optimism)

    async def refuel_to_avalanche(self):
        return await self._refuel(dest_network=SupportedNetworks.Avalanche)
