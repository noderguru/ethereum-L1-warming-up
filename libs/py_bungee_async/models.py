from dataclasses import dataclass
from typing import Optional, Dict, List, Union, Any

from libs.pretty_utils.miscellaneous.files import read_json
from libs.py_eth_async.data.models import Network, Networks, RawContract

from libs.py_bungee_async.data.config import ABIS_DIR


class ABIs:
    """
    An instance with contract ABIs.
    """
    Registry: list = read_json((ABIS_DIR, 'registry.json'))
    Refuel: list = read_json((ABIS_DIR, 'refuel.json'))


@dataclass
class SupportedNetwork:
    """
    An instance of a supported network.
    """
    network: Network
    registry: Optional[RawContract] = None
    refuel: Optional[RawContract] = None


class SupportedNetworks:
    """
    An instance with all supported networks.
    """
    __Registry: RawContract = RawContract(address='0xc30141B657f4216252dc59Af2e7CdB9D8792e1B0', abi=ABIs.Registry)

    Ethereum: Optional[SupportedNetwork] = SupportedNetwork(
        network=Networks.Ethereum, registry=__Registry,
        refuel=RawContract(address='0xb584D4bE1A5470CA1a8778E9B86c81e165204599', abi=ABIs.Refuel)
    )
    Optimism: Optional[SupportedNetwork] = SupportedNetwork(
        network=Networks.Optimism, registry=__Registry,
        refuel=RawContract(address='0x5800249621DA520aDFdCa16da20d8A5Fc0f814d8', abi=ABIs.Refuel)
    )
    BSC: Optional[SupportedNetwork] = SupportedNetwork(
        network=Networks.BSC, registry=__Registry,
        refuel=RawContract(address='0xBE51D38547992293c89CC589105784ab60b004A9', abi=ABIs.Refuel)
    )
    Gnosis: Optional[SupportedNetwork] = SupportedNetwork(
        network=Networks.Gnosis, registry=__Registry,
        refuel=RawContract(address='0xBE51D38547992293c89CC589105784ab60b004A9', abi=ABIs.Refuel)
    )
    Polygon: Optional[SupportedNetwork] = SupportedNetwork(
        network=Networks.Polygon, registry=__Registry,
        refuel=RawContract(address='0xAC313d7491910516E06FBfC2A0b5BB49bb072D91', abi=ABIs.Refuel)
    )
    Fantom: Optional[SupportedNetwork] = SupportedNetwork(
        network=Networks.Fantom, registry=__Registry,
        refuel=RawContract(address='0x040993fbF458b95871Cd2D73Ee2E09F4AF6d56bB', abi=ABIs.Refuel)
    )
    zkSync: Optional[SupportedNetwork] = SupportedNetwork(
        network=Network(
            name='zksync',
            rpc='https://mainnet.era.zksync.io',
            chain_id=324,
            tx_type=0,
            coin_symbol='ETH',
            explorer='https://explorer.zksync.io/',
        )
    )
    Arbitrum: Optional[SupportedNetwork] = SupportedNetwork(
        network=Networks.Arbitrum, registry=__Registry,
        refuel=RawContract(address='0xc0E02AA55d10e38855e13B64A8E1387A04681A00', abi=ABIs.Refuel)
    )
    Avalanche: Optional[SupportedNetwork] = SupportedNetwork(
        network=Networks.Avalanche,
        registry=RawContract(address='0x2b42AFFD4b7C14d9B7C2579229495c052672Ccd3', abi=ABIs.Registry),
        refuel=RawContract(address='0x040993fbF458b95871Cd2D73Ee2E09F4AF6d56bB', abi=ABIs.Refuel)
    )
    Aurora: Optional[SupportedNetwork] = None

    all_networks: Dict[int, SupportedNetwork] = {
        1: Ethereum,
        10: Optimism,
        56: BSC,
        100: Gnosis,
        137: Polygon,
        250: Fantom,
        324: zkSync,
        42161: Arbitrum,
        43114: Avalanche,
        # 1313161554: Aurora
    }


class Sort:
    """
    An instance with sorting route types.
    """
    Output = 'output'
    Time = 'time'


class ReprWithoutData:
    """
    Contains a __repr__ function that automatically builds the output of a class using all its variables except 'data'.
    """

    def __repr__(self) -> str:
        attributes = vars(self).copy()
        del attributes['data']
        values = ('{}={!r}'.format(key, value) for key, value in attributes.items())
        return '{}({})'.format(self.__class__.__name__, ', '.join(values))


class Route(ReprWithoutData):
    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize an instance of a route.

        Args:
            data (Dict[str, Any]): the dictionary with a route data.

        """
        self.data = data
        self.routeId: str = data.get('routeId')
        self.isOnlySwapRoute: bool = data.get('isOnlySwapRoute')
        self.fromAmount: int = int(data.get('fromAmount'))
        self.toAmount: int = int(data.get('toAmount'))
        self.usedBridgeNames: List[str] = data.get('usedBridgeNames')
        self.minimumGasBalances: Dict[str, str] = data.get('minimumGasBalances')
        self.chainGasBalances: Dict[str, Dict[str, Union[str, bool]]] = data.get('chainGasBalances')
        self.totalUserTx: int = int(data.get('totalUserTx'))
        self.sender: str = data.get('sender')
        self.recipient: str = data.get('recipient')
        self.totalGasFeesInUsd: float = float(data.get('totalGasFeesInUsd'))
        self.receivedValueInUsd: float = float(data.get('receivedValueInUsd'))
        self.userTxs: List[Dict[str, Any]] = data.get('userTxs')
        self.serviceTime: int = int(data.get('serviceTime'))
        self.maxServiceTime: int = int(data.get('maxServiceTime'))
        self.integratorFee: Dict[str, Any] = data.get('integratorFee')


class Quote(ReprWithoutData):
    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize an instance of a quote.

        Args:
            data (Dict[str, Any]): the dictionary with a quote data.

        """
        self.data = data
        self.routes: List[Route] = []
        self.refuel: Optional[Dict[str, Any]] = data.get('refuel')
        self.destinationCallData: Dict[str, Any] = data.get('destinationCallData')
        self.fromChainId: int = int(data.get('fromChainId'))
        self.fromAsset: Dict[str, Union[str, int]] = data.get('fromAsset')
        self.toChainId: int = int(data.get('toChainId'))
        self.toAsset: Dict[str, Union[str, int]] = data.get('toAsset')
        self.bridgeRouteErrors: Dict[str, Dict[str, str]] = data.get('bridgeRouteErrors')

        self.parse_routers(routes=data['routes'])

    def parse_routers(self, routes: Optional[List[Dict[str, Any]]]) -> None:
        """
        Convert dictionaries with route data to Route instances.

        Args:
            routes (Optional[List[Dict[str, Any]]]): a list with route dictionaries.

        """
        if not routes:
            return

        for route in routes:
            self.routes.append(Route(data=route))


class RefuelQuote(ReprWithoutData):
    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize an instance of a refuel quote.

        Args:
            data (Dict[str, Any]): the dictionary with a refuel quote data.

        """
        self.data = data
        self.estimatedOutput: int = int(data.get('estimatedOutput'))
        self.gasMovrFee: int = int(data.get('gasMovrFee'))
        self.destinationFee: int = int(data.get('destinationFee'))
        self.destinationToken: str = data.get('destinationToken')
        self.contractAddress: str = data.get('contractAddress')
        self.usdValues: Dict[str, float] = {}
        self.estimatedTime: int = int(data.get('estimatedTime'))

        for key, value in data.get('usdValues').items():
            self.usdValues[key] = float(value)
