import asyncio
from typing import Optional, Union, Dict

from fake_useragent import UserAgent
from libs.pretty_utils.miscellaneous.http import aiohttp_params
from libs.pretty_utils.type_functions.floats import randfloat
from libs.py_eth_async.client import Client
from libs.py_eth_async.data.models import Ether, TokenAmount, Wei, GWei, TxArgs
from libs.py_eth_async.data.types import Contract, Amount, GasPrice, GasLimit, Address
from libs.py_eth_async.transactions import Tx
from libs.py_token_contracts.tokens import ETH

from libs.py_bungee_async import exceptions
from libs.py_bungee_async.models import SupportedNetworks, SupportedNetwork, Quote, Sort, RefuelQuote
from libs.py_bungee_async.utils import async_post, async_get


class Bungee:
    """
    The client that is used to interact with the Bungee.

    Attributes:
        client (Client): an instance of a py-eth-async Client.
        network (SupportedNetwork): an instance of a supported network.
        headers (Dict[str, str]): headers for Bungee API requests.

    """
    client: Client
    network: SupportedNetwork
    headers: Dict[str, str]

    def __init__(self, client: Client) -> None:
        """
        Initialize the class.

        Args:
            client (Client): an instance of a py-eth-async Client.

        """
        if client.network.chain_id not in SupportedNetworks.all_networks:
            raise exceptions.UnsupportedNetwork

        self.client: Client = client
        self.network = SupportedNetworks.all_networks.get(client.network.chain_id)
        self.headers = {
            'authority': 'api-ms.socket.tech',
            'accept': '*/*',
            'api-key': '615deab3-3ead-4480-a59b-b0fc53d2d592',
            'origin': 'https://www.bungee.exchange',
            'referer': 'https://www.bungee.exchange/',
            'user-agent': UserAgent().chrome
        }

    @staticmethod
    async def is_eth(token: str) -> bool:
        """
        Check if the specified token is ETH.

        Args:
            token (str): a contract address of a token.

        Returns:
            bool: True if the token is ETH.

        """
        if token.lower() == ETH.Ethereum.lower():
            return True

        return False

    async def get_quote(
            self, source_token: Contract, amount: Amount, dest_network: SupportedNetwork, dest_token: Contract,
            source_network: Optional[SupportedNetwork] = None, from_: Optional[Address] = None,
            recipient: Optional[Address] = None, refuel: bool = False, slippage: Union[str, int] = 1,
            sort: str = Sort.Output
    ) -> Quote:
        """
        Find a quote with specified parameters.

        Args:
            source_token (Contract): a contract address or instance of the source token.
            amount (Amount): amount of the token to bridge.
            dest_network (SupportedNetwork): the SupportedNetwork instance of the destination network.
            dest_token (Contract): a contract address or instance of the destination token.
            source_network (Optional[SupportedNetwork]): the SupportedNetwork instance of the source
                network. (from the imported Client)
            from_ (Optional[Address]): the address from which the transaction will be sent. (from the imported Client)
            recipient (Optional[Address]): the token recipient. (matches 'from_')
            refuel (bool): whether coin need to be sent additionally to pay for gas in the destination network. (False)
            slippage (Union[str, int]): the swap slippage. (1%)
            sort (str): a sort type, either "output" or "time". ("output")

        Returns:
            Quote: the found quote.

        """
        if sort not in (Sort.Output, Sort.Time):
            raise exceptions.BungeeException('"sort" parameter have to be either "output" or "time"')

        if not source_network:
            source_network = self.network

        if not from_:
            from_ = self.client.account.address

        if not recipient:
            recipient = from_

        if isinstance(amount, (float, int)):
            if await self.is_eth(source_token):
                amount = Ether(amount=amount)

            else:
                contract = await self.client.contracts.default_token(contract_address=source_token)
                amount = TokenAmount(amount=amount, decimals=await contract.functions.decimals().call())

        params = {
            'fromChainId': source_network.network.chain_id,
            'fromTokenAddress': source_token.lower(),
            'fromAmount': amount.Wei,
            'toChainId': dest_network.network.chain_id,
            'toTokenAddress': dest_token.lower(),
            'userAddress': from_,
            'recipient': recipient,
            'singleTxOnly': True,
            'bridgeWithGas': refuel,
            'defaultSwapSlippage': slippage,
            'bridgeWithInsurance': True,
            'isContractCall': False,
            'sort': sort
        }

        response = await async_get(
            'https://api-ms.socket.tech/v2/quote', params=aiohttp_params(params), headers=self.headers,
            proxy=self.client.proxy
        )
        if response['success']:
            return Quote(data=response['result'])

        raise exceptions.APIException(response=response)

    async def get_min_max_amount(
            self,
            dest_network: SupportedNetwork,
            source_network: Optional[SupportedNetwork] = None
    ) -> tuple[int, int]:
        if not source_network:
            source_network = self.network

        response = await async_get(url='https://refuel.socket.tech/chains',
                                   headers=self.headers, proxy=self.client.proxy)

        min_amount = 0
        max_amount = 0
        for src_chain in response.get('result'):
            if src_chain['chainId'] == source_network.network.chain_id:
                for dest_chain in src_chain['limits']:
                    if dest_chain['chainId'] == dest_network.network.chain_id:
                        min_amount = int(dest_chain['minAmount'])
                        max_amount = int(dest_chain['maxAmount'])
        return min_amount, max_amount

    async def get_refuel_quote(
            self, amount: Amount, dest_network: SupportedNetwork, source_network: Optional[SupportedNetwork] = None
    ) -> RefuelQuote:
        """
        Find a refuel quote with specified parameters.

        Args:
            amount (Amount): amount of the token to bridge.
            dest_network (SupportedNetwork): the SupportedNetwork instance of the destination network.
            source_network (Optional[SupportedNetwork]): the SupportedNetwork instance of the source
                network. (from the imported Client)

        Returns:
            RefuelQuote: the found refuel quote.

        """
        if not source_network:
            source_network = self.network

        if isinstance(amount, (float, int)):
            amount = Ether(amount=amount)

        min_amount, max_amount = await self.get_min_max_amount(
            dest_network=dest_network,
            source_network=source_network
        )

        if amount < min_amount or amount > max_amount:
            raise exceptions.UnacceptableAmount

        params = {
            'fromChainId': source_network.network.chain_id,
            'amount': amount.Wei,
            'toChainId': dest_network.network.chain_id
        }

        response = await async_get(
            'https://refuel.socket.tech/quote', params=aiohttp_params(params), headers=self.headers,
            proxy=self.client.proxy
        )
        if response['success']:
            return RefuelQuote(data=response['result'])

        raise exceptions.APIException(response=response)

    async def bridge(
            self, source_token: Contract, dest_network: SupportedNetwork, dest_token: Contract,
            amount: Optional[Amount] = None, recipient: Optional[Address] = None, refuel: bool = False,
            slippage: Union[str, int] = 1, quote: Optional[Quote] = None,
            delay_after_approval: Optional[Union[int, float]] = None, gas_price: Optional[GasPrice] = None,
            gas_limit: Optional[GasLimit] = None, nonce: Optional[int] = None, check_gas_price: bool = False,
            dry_run: bool = False
    ) -> Tx:
        """

        Args:
            source_token (Contract): a contract address or instance of the source token.
            dest_network (SupportedNetwork): the SupportedNetwork instance of the destination network.
            dest_token (Contract): a contract address or instance of the destination token.
            amount (Optional[Amount]): amount of the token to bridge. (all balance)
            recipient (Optional[Address]): the token recipient. (from the imported Client)
            refuel (bool): whether coin need to be sent additionally to pay for gas in the destination network. (False)
            slippage (Union[str, int]): the swap slippage. (1%)
            quote (Optional[Quote]): a pre-selected quote. (parsed)
            delay_after_approval (Optional[Union[int, float]]): the delay between token approval and the
                next action. (3-5 sec)
            gas_price (Optional[GasPrice]): the gas price in GWei. (parsed from the network)
            gas_limit (Optional[GasLimit]): the gas limit in Wei. (parsed from the network)
            nonce (Optional[int]): a nonce of the sender address. (get it using the 'nonce' function)
            check_gas_price (bool): if True and the gas price is higher than that specified in the 'gas_price'
                argument, the 'GasPriceTooHigh' error will raise. (False)
            dry_run (bool): if True, it creates a parameter dictionary, but doesn't send the transaction. (False)

        Returns:
            Tx: the instance of the sent transaction.

        """
        # ----- Preparing
        if not recipient:
            recipient = self.client.account.address

        if await self.is_eth(source_token):
            balance = await self.client.wallet.balance()

        else:
            source_token, _ = await self.client.contracts.get_contract_attributes(contract=source_token)
            balance = await self.client.wallet.balance(token=source_token)

        if not await self.is_eth(dest_token):
            dest_token, _ = await self.client.contracts.get_contract_attributes(contract=dest_token)

        if isinstance(amount, (float, int)):
            if await self.is_eth(source_token):
                amount = Ether(amount=amount)

            else:
                contract = await self.client.contracts.default_token(contract_address=source_token)
                amount = TokenAmount(amount=amount, decimals=await contract.functions.decimals().call())

        elif not amount:
            if await self.is_eth(source_token):
                balance_quote = await self.get_quote(
                    source_token=source_token, amount=balance, dest_network=dest_network, dest_token=dest_token,
                    recipient=recipient, refuel=refuel, slippage=slippage
                )
                amount = balance - int(balance_quote.routes[0].chainGasBalances[str(self.network.network.chain_id)][
                                           'minGasBalance'])

            else:
                amount = balance

        if balance < amount:
            raise exceptions.InsufficientBalance('Insufficient balance to bridge.')

        if not quote:
            quote = await self.get_quote(
                source_token=source_token, amount=amount, dest_network=dest_network, dest_token=dest_token,
                recipient=recipient, refuel=refuel, slippage=slippage
            )

        if not quote.routes:
            raise exceptions.NoRoutes

        json_data = {
            'fromAssetAddress': quote.fromAsset['address'],
            'fromChainId': quote.fromAsset['chainId'],
            'toAssetAddress': quote.toAsset['address'],
            'toChainId': quote.toAsset['chainId'],
            'refuel': quote.refuel,
            'route': quote.routes[0].data,
            'sender': self.client.account.address
        }

        response = await async_post(
            'https://api-ms.socket.tech/v2/route/start', json=json_data, headers=self.headers, proxy=self.client.proxy
        )

        # ----- Approve
        params = {
            'activeRouteId': response['result']['activeRouteId'],
            'swapSlippage': slippage
        }
        response = await async_get(
            'https://api-ms.socket.tech/v2/route/build-next-tx', params=params, headers=self.headers,
            proxy=self.client.proxy
        )
        result = response['result']
        approval_data = result['approvalData']
        if approval_data:
            approval_token = approval_data.get('approvalTokenAddress')
            spender = approval_data.get('allowanceTarget')
            approved_amount = await self.client.transactions.approved_amount(token=approval_token, spender=spender)
            if approved_amount.Wei < int(approval_data.get('minimumApprovalAmount')):
                if dry_run:
                    print(f'At this point the spending {approval_token} by {spender} will be approved...')

                else:
                    approval_tx = await self.client.transactions.approve(token=approval_token, spender=spender)
                    try:
                        await approval_tx.wait_for_receipt(client=self.client)

                    except:
                        raise exceptions.FailedToApprove

                    if delay_after_approval:
                        await asyncio.sleep(delay_after_approval)

                    else:
                        await asyncio.sleep(randfloat(from_=3.0, to_=5.0))

        # ----- Construct transaction
        current_gas_price = await self.client.transactions.gas_price()
        if not gas_price:
            gas_price = current_gas_price

        elif gas_price:
            if isinstance(gas_price, (int, float)):
                gas_price = GWei(gas_price)

        if check_gas_price and current_gas_price > gas_price:
            raise exceptions.GasPriceTooHigh

        if not nonce:
            nonce = await self.client.wallet.nonce()

        tx_params = {
            'chainId': result.get('chainId'),
            'nonce': nonce,
            'from': self.client.account.address,
            'to': result.get('txTarget'),
            'data': result.get('txData'),
            'value': int(result.get('value'), 16)
        }

        # General
        if self.client.network.tx_type == 2:
            tx_params['maxFeePerGas'] = gas_price.Wei
            tx_params['maxPriorityFeePerGas'] = (await self.client.transactions.max_priority_fee(w3=self.client.w3)).Wei

        else:
            tx_params['gasPrice'] = gas_price.Wei

        if not gas_limit:
            gas_limit = await self.client.transactions.estimate_gas(w3=self.client.w3, tx_params=tx_params)

        elif isinstance(gas_limit, int):
            gas_limit = Wei(gas_limit)

        tx_params['gas'] = gas_limit.Wei
        if dry_run:
            return Tx(params=tx_params)

        return await self.client.transactions.sign_and_send(tx_params=tx_params)

    async def refuel(self, dest_network: SupportedNetwork, amount: Optional[Amount] = None,
                     gas_price: Optional[GasPrice] = None, gas_limit: Optional[GasLimit] = None,
                     nonce: Optional[int] = None, check_gas_price: bool = False, dry_run: bool = False) -> Tx:
        """
        Refuel coin from one network to another.

        Args:
            dest_network (SupportedNetwork): the SupportedNetwork instance of the destination network.
            amount (Optional[Amount]): amount of the token to bridge. (all balance)
            gas_price (Optional[GasPrice]): the gas price in GWei. (parsed from the network)
            gas_limit (Optional[GasLimit]): the gas limit in Wei. (parsed from the network)
            nonce (Optional[int]): a nonce of the sender address. (get it using the 'nonce' function)
            check_gas_price (bool): if True and the gas price is higher than that specified in the 'gas_price'
                argument, the 'GasPriceTooHigh' error will raise. (False)
            dry_run (bool): if True, it creates a parameter dictionary, but doesn't send the transaction. (False)

        Returns:
            Tx: the instance of the sent transaction.

        """
        # ----- Preparing
        balance = await self.client.wallet.balance()
        if isinstance(amount, (float, int)):
            amount = Ether(amount=amount)

        elif not amount:
            amount = balance

        if balance < amount:
            raise exceptions.InsufficientBalance('Insufficient balance to bridge.')

        await self.get_refuel_quote(amount=amount, dest_network=dest_network)

        # ----- Construct transaction
        current_gas_price = await self.client.transactions.gas_price()
        if not gas_price:
            gas_price = current_gas_price

        elif gas_price:
            if isinstance(gas_price, (int, float)):
                gas_price = GWei(gas_price)

        if check_gas_price and current_gas_price > gas_price:
            raise exceptions.GasPriceTooHigh

        if not nonce:
            nonce = await self.client.wallet.nonce()

        args = TxArgs(
            destinationChainId=dest_network.network.chain_id,
            _to=self.client.account.address
        )

        contract = await self.client.contracts.get(self.network.refuel)
        tx_params = {
            'chainId': self.network.network.chain_id,
            'nonce': nonce,
            'from': self.client.account.address,
            'to': contract.address,
            'data': contract.encodeABI('depositNativeToken', args=args.tuple()),
            'value': amount.Wei
        }

        # General
        if self.client.network.tx_type == 2:
            # tx_params['maxFeePerGas'] = gas_price.Wei
            # tx_params['maxPriorityFeePerGas'] = (await self.client.transactions.max_priority_fee(w3=self.client.w3)).Wei

            tx_params['maxPriorityFeePerGas'] = (await self.client.transactions.max_priority_fee(w3=self.client.w3)).Wei
            last_block = await self.client.w3.eth.get_block('latest')
            tx_params['maxFeePerGas'] = last_block['baseFeePerGas'] + tx_params['maxPriorityFeePerGas']

        else:
            tx_params['gasPrice'] = gas_price.Wei

        if not gas_limit:
            gas_limit = await self.client.transactions.estimate_gas(w3=self.client.w3, tx_params=tx_params)

        elif isinstance(gas_limit, int):
            gas_limit = Wei(gas_limit)

        tx_params['gas'] = gas_limit.Wei
        if dry_run:
            return Tx(params=tx_params)

        return await self.client.transactions.sign_and_send(tx_params=tx_params)
