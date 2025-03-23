from loguru import logger

from tasks.base import Base
from data.models import Contracts


class L2Marathon(Base):
    async def _mint(self):
        router = await self.client.contracts.get(contract_address=Contracts.L2MARATHON)
        fee = await router.functions.fee().call()
        tx_params = {
            'to': router.address,
            'data': router.encodeABI('mint', args=()),
            'value': fee
        }
        tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
        receipt = await tx.wait_for_receipt(client=self.client, timeout=300)

        if receipt:
            return tx

    async def mint(self):
        failed_text = 'Failed to mint NFT on l2marathon'
        try:
            logger.info(f'{self.client.account.address} | start mint NFT on l2marathon')

            if tx := await self._mint():
                return f'Successfully mint NFT on l2marathon: {tx.hash.hex()}'
            return failed_text

        except BaseException as e:
            return f'{failed_text}: {e}'
