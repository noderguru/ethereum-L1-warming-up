from loguru import logger

from libs.py_eth_async.transactions import Tx
from libs.py_eth_async.data.models import Unit, TokenAmount, TxArgs

from tasks.base import Base
from data.models import Settings, Contracts


class ETHWrapper(Base):
    async def _wrap(self, amount: Unit | TokenAmount) -> Tx | None:
        contract = await self.client.contracts.get(contract_address=Contracts.WETH)
        tx_params = {
            'to': contract.address,
            'data': contract.encodeABI('deposit'),
            'value': amount.Wei
        }

        tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
        receipt = await tx.wait_for_receipt(client=self.client, timeout=300)

        if receipt:
            return tx

    async def _unwrap(self, amount: Unit | TokenAmount | None = None) -> Tx | None:
        contract = await self.client.contracts.get(contract_address=Contracts.WETH)

        if not amount:
            amount = await self.client.wallet.balance(token=Contracts.WETH)

        args = TxArgs(
            wad=amount.Wei
        )

        tx_params = {
            'to': contract.address,
            'data': contract.encodeABI('withdraw', args=args.tuple()),
        }

        tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
        receipt = await tx.wait_for_receipt(client=self.client, timeout=300)

        if receipt:
            return tx

    async def wrap(self) -> str:
        failed_text = 'Failed to wrap ETH'
        settings = Settings()

        try:
            balance = await self.client.wallet.balance()
            amount = self.get_random_eth_amount_by_balance(balance=balance)

            logger.info(f'{self.client.account.address} | eth -> weth')

            if balance < amount + settings.minimal_balance:
                return f'{failed_text}: insufficient balance.'

            if tx := await self._wrap(amount=amount):
                return f'ETH was wrapped: {tx.hash.hex()}'
            return failed_text

        except BaseException as e:
            return f'{failed_text}: {e}'

    async def unwrap(self) -> str:
        failed_text = 'Failed to unwrap ETH'

        try:
            logger.info(f'{self.client.account.address} | weth -> eth')

            weth_balance = await self.client.wallet.balance(token=Contracts.WETH)
            if not weth_balance:
                return f'{failed_text}: insufficient balance.'

            if tx := await self._unwrap(amount=weth_balance):
                return f'ETH was unwrapped: {tx.hash.hex()}'
            return failed_text

        except BaseException as e:
            return f'{failed_text}: {e}'
