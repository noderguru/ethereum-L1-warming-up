from loguru import logger
import asyncio
import time

from eth_typing import ChecksumAddress
from web3 import Web3

from libs.py_eth_async.data.models import TxArgs, Unit, TokenAmount
from libs.pretty_utils.type_functions.floats import randfloat
from tasks.base import Base
from data.models import Settings, Contracts


class Shibaswap(Base):
    async def _swap(self, path: list[ChecksumAddress | str], amount: Unit, slippage=1):
        path = list(map(lambda p: Web3.to_checksum_address(p), path))

        router = await self.client.contracts.get(contract_address=Contracts.SHIBASWAP)

        from_token_contract = await self.client.contracts.default_token(contract_address=path[0])
        to_token_contract = await self.client.contracts.default_token(contract_address=path[1])

        from_token_name = await from_token_contract.functions.symbol().call()
        to_token_name = await to_token_contract.functions.symbol().call()

        to_token_decimals = await to_token_contract.functions.decimals().call()

        from_token_price_dollar = await Shibaswap.get_token_price(token_symbol=from_token_name)
        to_token_price_dollar = await Shibaswap.get_token_price(token_symbol=to_token_name)

        amount_out_min = TokenAmount(
            amount=float(amount.Ether) * from_token_price_dollar / to_token_price_dollar * (
                        100 - slippage) / 100,
            decimals=to_token_decimals
        )

        logger.info(f'Start swap {amount.Ether} {from_token_name} to {amount_out_min.Ether} {to_token_name}')

        if path[0] == Contracts.WETH.address:
            args = TxArgs(
                amountOutMin=amount_out_min.Wei,
                path=path,
                to=self.client.account.address,
                deadline=int(time.time() + 1200)
            )
        else:
            approved_amount = await self.client.transactions.approved_amount(token=from_token_contract, spender=router)
            if amount.Wei > approved_amount.Wei:
                # approve
                await self.client.transactions.approve(token=from_token_contract, spender=router, amount=amount)
                await asyncio.sleep(5)

            args = TxArgs(
                amountIn=amount.Wei,
                amountOutMin=amount_out_min.Wei,
                path=path,
                to=self.client.account.address,
                deadline=int(time.time() + 1200)
            )

        function_name = 'swapExactETHForTokens' if path[0] == Contracts.WETH.address else 'swapExactTokensForETH'
        value = amount.Wei if path[0] == Contracts.WETH.address else 0

        tx_params = {
            'to': router.address,
            'data': router.encodeABI(function_name, args=args.tuple()),
            'value': value
        }

        tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
        receipt = await tx.wait_for_receipt(client=self.client, timeout=300)

        if receipt:
            return tx

    async def swap_eth_to_usdc(self):
        failed_text = 'Failed to swap ETH to USDC via ShibaSwap'
        settings = Settings()

        try:
            balance = await self.client.wallet.balance()
            amount = self.get_random_eth_amount_by_balance(balance=balance)

            logger.info(f'{self.client.account.address} | {amount.Ether} ETH -> USDC via SushiSwap')

            if balance < amount + settings.minimal_balance:
                return f'{failed_text}: insufficient balance.'

            path = [Contracts.WETH.address, Contracts.USDC.address]

            if tx := await self._swap(path=path, amount=amount):
                return f'{amount.Ether} ETH was swapped to USDC via SushiSwap: {tx.hash.hex()}'
            return failed_text

        except BaseException as e:
            return f'{failed_text}: {e}'

    async def swap_eth_to_usdt(self):
        failed_text = 'Failed to swap ETH to USDT via ShibaSwap'
        settings = Settings()

        try:
            balance = await self.client.wallet.balance()
            amount = self.get_random_eth_amount_by_balance(balance=balance)

            logger.info(f'{self.client.account.address} | {amount.Ether} ETH -> USDT via SushiSwap')

            if balance < amount + settings.minimal_balance:
                return f'{failed_text}: insufficient balance.'

            path = [Contracts.WETH.address, Contracts.USDT.address]

            if tx := await self._swap(path=path, amount=amount):
                return f'{amount.Ether} ETH was swapped to USDT via SushiSwap: {tx.hash.hex()}'
            return failed_text

        except BaseException as e:
            return f'{failed_text}: {e}'

    async def swap_eth_to_dai(self):
        failed_text = 'Failed to swap ETH to DAI via ShibaSwap'
        settings = Settings()

        try:
            balance = await self.client.wallet.balance()
            amount = self.get_random_eth_amount_by_balance(balance=balance)

            logger.info(f'{self.client.account.address} | {amount.Ether} ETH -> DAI via SushiSwap')

            if balance < amount + settings.minimal_balance:
                return f'{failed_text}: insufficient balance.'

            path = [Contracts.WETH.address, Contracts.DAI.address]

            if tx := await self._swap(path=path, amount=amount):
                return f'{amount.Ether} ETH was swapped to DAI via SushiSwap: {tx.hash.hex()}'
            return failed_text

        except BaseException as e:
            return f'{failed_text}: {e}'

    async def swap_eth_to_wbtc(self):
        failed_text = 'Failed to swap ETH to WBTC via ShibaSwap'
        settings = Settings()

        try:
            balance = await self.client.wallet.balance()
            amount = self.get_random_eth_amount_by_balance(balance=balance)

            logger.info(f'{self.client.account.address} | {amount.Ether} ETH -> WBTC via SushiSwap')

            if balance < amount + settings.minimal_balance:
                return f'{failed_text}: insufficient balance.'

            path = [Contracts.WETH.address, Contracts.WBTC.address]

            if tx := await self._swap(path=path, amount=amount):
                return f'{amount.Ether} ETH was swapped to WBTC via SushiSwap: {tx.hash.hex()}'
            return failed_text

        except BaseException as e:
            return f'{failed_text}: {e}'

    async def swap_usdc_to_eth(self):
        failed_text = 'Failed to swap USDC to ETH via ShibaSwap'
        settings = Settings()
        token = Contracts.USDC

        try:
            token_contract = await self.client.contracts.default_token(contract_address=token)
            token_balance = await self.client.wallet.balance(token)
            token_decimals = await token_contract.functions.decimals().call()
            amount_in_eth = randfloat(
                from_=settings.eth_amount_for_swap.from_,
                to_=settings.eth_amount_for_swap.to_,
                step=0.0000001
            )

            eth_price = await Shibaswap.get_token_price()
            token_price = await Shibaswap.get_token_price(token_symbol=token.title)
            amount = TokenAmount(
                amount=token_price / eth_price * amount_in_eth,
                decimals=token_decimals
            )
            if amount.Wei < token_balance.Wei:
                amount = token_balance

            logger.info(f'{self.client.account.address} | {amount.Ether} {token.title} -> ETH via SushiSwap')

            path = [Contracts.USDC.address, Contracts.WETH.address]

            if tx := await self._swap(path=path, amount=amount):
                return f'{amount.Ether} {token.title} was swapped to ETH via SushiSwap: {tx.hash.hex()}'
            return failed_text

        except BaseException as e:
            return f'{failed_text}: {e}'

    async def swap_usdt_to_eth(self):
        failed_text = 'Failed to swap USDT to ETH via ShibaSwap'
        settings = Settings()
        token = Contracts.USDT

        try:
            token_contract = await self.client.contracts.default_token(contract_address=token)
            token_balance = await self.client.wallet.balance(token)
            token_decimals = await token_contract.functions.decimals().call()
            amount_in_eth = randfloat(
                from_=settings.eth_amount_for_swap.from_,
                to_=settings.eth_amount_for_swap.to_,
                step=0.0000001
            )

            eth_price = await Shibaswap.get_token_price()
            token_price = await Shibaswap.get_token_price(token_symbol=token.title)
            amount = TokenAmount(
                amount=token_price / eth_price * amount_in_eth,
                decimals=token_decimals
            )
            if amount.Wei < token_balance.Wei:
                amount = token_balance

            logger.info(f'{self.client.account.address} | {amount.Ether} {token.title} -> ETH via SushiSwap')

            path = [Contracts.USDT.address, Contracts.WETH.address]

            if tx := await self._swap(path=path, amount=amount):
                return f'{amount.Ether} {token.title} was swapped to ETH via SushiSwap: {tx.hash.hex()}'
            return failed_text

        except BaseException as e:
            return f'{failed_text}: {e}'

    async def swap_dai_to_eth(self):
        failed_text = 'Failed to swap DAI to ETH via ShibaSwap'
        settings = Settings()
        token = Contracts.DAI

        try:
            token_contract = await self.client.contracts.default_token(contract_address=token)
            token_balance = await self.client.wallet.balance(token)
            token_decimals = await token_contract.functions.decimals().call()
            amount_in_eth = randfloat(
                from_=settings.eth_amount_for_swap.from_,
                to_=settings.eth_amount_for_swap.to_,
                step=0.0000001
            )

            eth_price = await Shibaswap.get_token_price()
            token_price = await Shibaswap.get_token_price(token_symbol=token.title)
            amount = TokenAmount(
                amount=token_price / eth_price * amount_in_eth,
                decimals=token_decimals
            )
            if amount.Wei < token_balance.Wei:
                amount = token_balance

            logger.info(f'{self.client.account.address} | {amount.Ether} {token.title} -> ETH via SushiSwap')

            path = [Contracts.DAI.address, Contracts.WETH.address]

            if tx := await self._swap(path=path, amount=amount):
                return f'{amount.Ether} {token.title} was swapped to ETH via SushiSwap: {tx.hash.hex()}'
            return failed_text

        except BaseException as e:
            return f'{failed_text}: {e}'

    async def swap_wbtc_to_eth(self):
        failed_text = 'Failed to swap WBTC to ETH via ShibaSwap'
        settings = Settings()
        token = Contracts.WBTC

        try:
            token_contract = await self.client.contracts.default_token(contract_address=token)
            token_balance = await self.client.wallet.balance(token)
            token_decimals = await token_contract.functions.decimals().call()
            amount_in_eth = randfloat(
                from_=settings.eth_amount_for_swap.from_,
                to_=settings.eth_amount_for_swap.to_,
                step=0.0000001
            )

            eth_price = await Shibaswap.get_token_price()
            token_price = await Shibaswap.get_token_price(token_symbol=token.title)
            amount = TokenAmount(
                amount=token_price / eth_price * amount_in_eth,
                decimals=token_decimals
            )
            if amount.Wei < token_balance.Wei:
                amount = token_balance

            logger.info(f'{self.client.account.address} | {amount.Ether} {token.title} -> ETH via SushiSwap')

            path = [Contracts.WBTC.address, Contracts.WETH.address]

            if tx := await self._swap(path=path, amount=amount):
                return f'{amount.Ether} {token.title} was swapped to ETH via SushiSwap: {tx.hash.hex()}'
            return failed_text

        except BaseException as e:
            return f'{failed_text}: {e}'
