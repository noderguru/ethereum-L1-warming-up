from loguru import logger

from libs.py_eth_async.transactions import Tx
from libs.py_eth_async.data.models import Unit, TxArgs, TokenAmount

from tasks.base import Base
from data.models import Settings, Contracts


class Blur(Base):
    async def _deposit(self, amount: Unit | TokenAmount) -> Tx | None:
        contract = await self.client.contracts.get(contract_address=Contracts.BLUR)
        tx_params = {
            'to': contract.address,
            'data': contract.encodeABI('deposit'),
            'value': amount.Wei
        }

        tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
        receipt = await tx.wait_for_receipt(client=self.client, timeout=300)

        if receipt:
            return tx

    async def _withdraw(self, amount: Unit | TokenAmount | None = None) -> Tx | None:
        contract = await self.client.contracts.get(contract_address=Contracts.BLUR)

        eth_balance_on_blur = await self.client.wallet.balance(token=Contracts.BLUR)
        if not amount or eth_balance_on_blur.Wei < amount.Wei:
            amount = eth_balance_on_blur

        args = TxArgs(
            amount=amount.Wei
        )

        tx_params = {
            'to': contract.address,
            'data': contract.encodeABI('withdraw', args=args.tuple()),
        }

        tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
        receipt = await tx.wait_for_receipt(client=self.client, timeout=300)

        if receipt:
            return tx

    async def deposit(self) -> str:
        failed_text = 'Failed to deposit ETH to Blur'
        settings = Settings()

        try:
            balance = await self.client.wallet.balance()
            amount = self.get_random_eth_amount_by_balance(balance=balance)

            logger.info(f'{self.client.account.address} | try to deposit {amount.Ether} ETH to Blur')

            if balance < amount + settings.minimal_balance:
                return f'{failed_text}: insufficient balance.'

            if tx := await self._deposit(amount=amount):
                return f'{amount.Ether} ETH was deposit to Blur: {tx.hash.hex()}'
            return failed_text

        except BaseException as e:
            return f'{failed_text}: {e}'

    async def withdraw(self) -> str:
        failed_text = 'Failed to withdraw ETH from Blur'
        settings = Settings()

        try:
            logger.info(f'{self.client.account.address} | try to withdraw ETH from Blur')

            amount = self.get_random_amount(
                from_=settings.eth_amount_for_swap.from_,
                to_=settings.eth_amount_for_swap.to_
            )

            if tx := await self._withdraw(amount=amount):
                return f'ETH was withdraw from Blur: {tx.hash.hex()}'
            return failed_text

        except BaseException as e:
            return f'{failed_text}: {e}'
