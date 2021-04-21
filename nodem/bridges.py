from nodem.entities import Broker

from commlib.bridges import (TopicBridge as CommTopBridge, TopicBridgeType,
                             RPCBridge as CommRPCBridge, RPCBridgeType)


class BaseBridge:
    def __init__(self, name: str, brokerA: Broker, brokerB: Broker):
        self.name = name
        self.brokerA = brokerA
        self.brokerB = brokerB

    def _create_commlib_bridge(self, commlib_bridge_class, bridge_type_class,
                               from_uri: str, to_uri: str):
        bridge_type = getattr(bridge_type_class,
                              f'{self.brokerA.type}_TO_{self.brokerB.type}')
        return commlib_bridge_class(
            bridge_type,
            from_uri=from_uri,
            to_uri=to_uri,
            from_broker_params=self.brokerA.connection_params,
            to_broker_params=self.brokerB.connection_params)


class TopicBridge(BaseBridge):
    def __init__(self, from_topic: str, to_topic: str, *args, **kwargs):
        self.from_topic = from_topic
        self.to_topic = to_topic
        super(TopicBridge, self).__init__(*args, **kwargs)

        self.commlib_bridge = self._create_commlib_bridge(CommTopBridge,
                                                          TopicBridgeType,
                                                          from_topic, to_topic)

    def __repr__(self):
        return f'Topic bridge {self.brokerA}-{self.brokerB}'


class RPCBridge(BaseBridge):
    def __init__(self, nameA: str, nameB: str, *args, **kwargs):
        self.nameA = nameA
        self.nameB = nameB
        super(RPCBridge, self).__init__(*args, **kwargs)

        self.commlib_bridge = self._create_commlib_bridge(CommRPCBridge,
                                                          RPCBridgeType, nameA,
                                                          nameB)

    def __repr__(self):
        return f'RPC bridge {self.brokerA}-{self.brokerB}'
