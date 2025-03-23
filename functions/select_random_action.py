import random

from loguru import logger

from tasks.controller import Controller
from utils.db_api.models import Wallet
from data.models import Settings, Contracts


async def select_random_action(controller: Controller, wallet: Wallet, initial: bool = False):
    settings = Settings()

    possible_actions = []
    weights = []

    wrap_unwrap_eth = 0
    swaps = 0
    telepathy = 0
    bungee = 0
    blur = 0

    l2marathon_contract = await controller.client.contracts.get(contract_address=Contracts.L2MARATHON)
    l2marathon_nft_amount = await l2marathon_contract.functions.balanceOf(controller.client.account.address).call()

    merkly_contract = await controller.client.contracts.get(contract_address=Contracts.MERKLY)
    merkly_nft_amount = await merkly_contract.functions.balanceOf(controller.client.account.address).call()

    eth_balance = await controller.client.wallet.balance()

    if float(eth_balance.Ether) < settings.minimal_balance:
        return 'Insufficient balance'

    if initial:
        coin_txs = (await controller.client.network.api.functions.account.txlist(
            address=controller.client.account.address
        ))['result']

        wrap_unwrap_eth = await controller.count_wrap_unwrap_eth(coin_txs=coin_txs)
        swaps = await controller.count_swaps(coin_txs=coin_txs)
        telepathy = await controller.count_telepathy(coin_txs=coin_txs)
        bungee = await controller.count_bungee(coin_txs=coin_txs)
        blur = await controller.count_blur_dep_wd(coin_txs=coin_txs)

        logger.debug(
            f'{wallet.address} | amount wrap_unwrap_eth: {wrap_unwrap_eth}/{wallet.number_of_wrap_unwrap_eth}; '
            f'amount swaps: {swaps}/{wallet.number_of_swaps}; '
            f'amount telepathy: {telepathy}/{wallet.number_of_telepathy}; '
            f'amount bungee: {bungee}/{wallet.number_of_bungee}; '
            f'amount blur: {blur}/{wallet.number_of_blur}; '
            f'amount l2marathon NFT: {l2marathon_nft_amount}/{wallet.number_of_l2marathon_nft}; '
            f'amount merkly NFT: {merkly_nft_amount}/{wallet.number_of_merkly_nft}; '
        )

        if (
                wrap_unwrap_eth >= wallet.number_of_wrap_unwrap_eth and
                telepathy >= wallet.number_of_telepathy and
                bungee >= wallet.number_of_bungee and
                blur >= wallet.number_of_blur and
                swaps >= wallet.number_of_swaps and
                l2marathon_nft_amount >= wallet.number_of_l2marathon_nft and
                merkly_nft_amount >= wallet.number_of_merkly_nft
        ):
            return 'Processed'

    sufficient_balance = float(eth_balance.Ether) > settings.minimal_balance + settings.eth_amount_for_swap.from_
    weth_balance = await controller.client.wallet.balance(token=Contracts.WETH)
    usdc_balance = await controller.client.wallet.balance(token=Contracts.USDC)
    usdt_balance = await controller.client.wallet.balance(token=Contracts.USDT)
    dai_balance = await controller.client.wallet.balance(token=Contracts.DAI)
    wbtc_balance = await controller.client.wallet.balance(token=Contracts.WBTC)
    eth_balance_on_blur = await controller.client.wallet.balance(token=Contracts.BLUR)

    if wrap_unwrap_eth < wallet.number_of_wrap_unwrap_eth:
        if sufficient_balance:
            possible_actions += [
                controller.eth_wrapper.wrap,
            ]
            weights += [
                1,
            ]
        if weth_balance.Wei:
            possible_actions += [
                controller.eth_wrapper.unwrap,
            ]
            weights += [
                1,
            ]

    if swaps < wallet.number_of_swaps:
        if sufficient_balance:
            possible_actions += [
                controller.shibaswap.swap_eth_to_usdc,
                controller.shibaswap.swap_eth_to_usdt,
                controller.shibaswap.swap_eth_to_dai,
                controller.shibaswap.swap_eth_to_wbtc,
            ]
            weights += [
                1,
                1,
                1,
                1,
            ]
        if usdc_balance.Wei:
            possible_actions += [
                controller.shibaswap.swap_usdc_to_eth,
            ]
            weights += [
                1,
            ]
        if usdt_balance.Wei:
            possible_actions += [
                controller.shibaswap.swap_usdt_to_eth,
            ]
            weights += [
                1,
            ]
        if dai_balance.Wei:
            possible_actions += [
                controller.shibaswap.swap_dai_to_eth,
            ]
            weights += [
                1,
            ]
        if wbtc_balance.Wei:
            possible_actions += [
                controller.shibaswap.swap_wbtc_to_eth,
            ]
            weights += [
                1,
            ]

    if telepathy < wallet.number_of_telepathy:
        if sufficient_balance:
            possible_actions += [
                controller.telepathy.send_mail_to_arbitrum,
                controller.telepathy.send_mail_to_avalanche,
                controller.telepathy.send_mail_to_polygon,
                controller.telepathy.send_mail_to_bsc,
                controller.telepathy.send_mail_to_goerli,
                controller.telepathy.send_mail_to_optimism,
                controller.telepathy.send_mail_to_gnosis,
            ]
            weights += [
                1,
                1,
                1,
                1,
                1,
                1,
                1,
            ]

    if bungee < wallet.number_of_bungee:
        if sufficient_balance:
            possible_actions += [
                controller.bungee.refuel_to_gnosis,
                controller.bungee.refuel_to_polygon,
                controller.bungee.refuel_to_zksync,
                controller.bungee.refuel_to_optimism,
                controller.bungee.refuel_to_avalanche,
            ]
            weights += [
                1,
                1,
                1,
                1,
                1,
            ]

    if blur < wallet.number_of_blur:
        if sufficient_balance:
            possible_actions += [
                controller.blur.deposit,
            ]
            weights += [
                1,
            ]
        if eth_balance_on_blur.Wei:
            possible_actions += [
                controller.blur.withdraw,
            ]
            weights += [
                1,
            ]

    if l2marathon_nft_amount < wallet.number_of_l2marathon_nft:
        if float(eth_balance.Ether) > settings.minimal_balance:
            possible_actions += [
                controller.l2marathon.mint,
            ]
            weights += [
                1,
            ]

    if merkly_nft_amount < wallet.number_of_merkly_nft:
        if float(eth_balance.Ether) > settings.minimal_balance:
            possible_actions += [
                controller.merkly.mint,
            ]
            weights += [
                1,
            ]

    if possible_actions:
        action = None
        while not action:
            action = random.choices(possible_actions, weights=weights)[0]

        else:
            return action

    return None
