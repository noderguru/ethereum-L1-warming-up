from loguru import logger

from web3 import Web3
from faker import Faker

from libs.py_eth_async.data.models import Ether
from libs.py_eth_async.transactions import Tx
from libs.py_eth_async.data.models import TxArgs, Networks, Network

from tasks.base import Base
from data.models import Settings, Contracts


class Telepathy(Base):
    MAILBOX_ADDRESS = Web3.to_checksum_address('0xF8f0929809fe4c73248C27DA0827C98bbE243FCc')

    @staticmethod
    def get_random_sentence():
        return Faker().sentence()

    async def send_mail(self, to_network: Network, msg: str) -> Tx | None:
        contract = await self.client.contracts.get(contract_address=Contracts.TELEPATHY)

        byte_str = msg.encode('utf-8')
        hexed_msg = '0x' + byte_str.hex()

        args = TxArgs(
            _destinationChainId=to_network.chain_id,
            _destinationMailbox=Telepathy.MAILBOX_ADDRESS,
            _message=hexed_msg,
        )

        tx_params = {
            'to': contract.address,
            'data': contract.encodeABI('sendMail', args=args.tuple()),
        }

        tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
        receipt = await tx.wait_for_receipt(client=self.client, timeout=300)

        if receipt:
            return tx

    async def send_mail_interface(self, to_network: Network):
        failed_text = f'Failed to send mail to {to_network.name} via telepathy'

        try:
            msg = Telepathy.get_random_sentence()
            logger.info(f'{self.client.account.address} | start send mail "{msg}" to {to_network.name} via telepathy')

            if tx := await self.send_mail(to_network=to_network, msg=msg):
                return f'mail "{msg}" was send to {to_network.name}: {tx.hash.hex()}'
            return failed_text

        except BaseException as e:
            return f'{failed_text}: {e}'

    async def send_mail_to_arbitrum(self) -> str:
        return await self.send_mail_interface(to_network=Networks.Arbitrum)

    async def send_mail_to_avalanche(self) -> str:
        return await self.send_mail_interface(to_network=Networks.Avalanche)

    async def send_mail_to_polygon(self) -> str:
        return await self.send_mail_interface(to_network=Networks.Polygon)

    async def send_mail_to_bsc(self) -> str:
        return await self.send_mail_interface(to_network=Networks.BSC)

    async def send_mail_to_goerli(self) -> str:
        return await self.send_mail_interface(to_network=Networks.Goerli)

    async def send_mail_to_optimism(self) -> str:
        return await self.send_mail_interface(to_network=Networks.Optimism)

    async def send_mail_to_gnosis(self) -> str:
        return await self.send_mail_interface(to_network=Networks.Gnosis)
