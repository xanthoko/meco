# MECO 
A library built upon MDE methodologies for modeling the entities and the communications of asynchronous message-driven systems.

<figure>
  <img src="images/meco_system.png" alt="Trulli" width="350">
  <figcaption><i>Overview of the described systems</i></figcaption>
</figure>


MECO provides a DSL (Domain Specific Language) for defining the entities and the ports that transfer the messages through the system. It references comm-idl, a DSL for defining the data models of the messages and broker-dsl, a DSL for defining the connection parameters with the brokers.

Currently the supported message transfer protocols are:
- AMPQ
- MQTT
- REDIS

and the implemented communication patterns are:
- pub-sub
- RPC


## How it works
### Syntax
The syntax of the model definitions is governed by 3 rules
1. Assignment of a value, declared by the character ":". The attribute can have a single value or other attributes as value. A publisher is defined as below

    ```
    publisher:
        topic: room.temperature
        frequency: 1
    ```
    Where topic has the single value of "room.temperature" and publisher has two attributes; topic and frequency.

2. Assignment of a list of values, declared by the character "-". For example, the definition of an output port looks like this.
    ```
    outports:
        - publisher
        - rpc_client secoRPC
    ```

3. Declaration of an object. The object type precedes the object name and then follow its attributes inside of "{}". For example, a node is defined as below
    ```
    Node CapeCanaveralPC {
        outports:
            - publisher:
                topic: shuttle.liftoff
                message: SpaceShuttleMsg
                frequency: 10
            - rpc_client secoRPC:
                message: SECOMsg
        inports:
            - subscriber:
                topic: countdown.left
    }
    ```

### Broker Definition
Broker models are defined according to the broker-dsl grammar.
```
brokerType brokerName -> {
    attributes
}
```
The possible values of brokerType are: "RabbitBroker", "AMQPBroker", "MQTTBroker", "EMQXBroker" and "RedisBroker". The attributes of each broker can be found in this repo https://github.com/robotics-4-all/broker-dsl

### Message Definition
The properties of the messages can be either a simple property declared like this `name: type default_value` or a list property declared like this `name: type[] default_value`. In both cases, *type* is a primitive data type (string, integer, float, boolean) or an Object defined in comm-idl as follows
```
Object name{
    properties
}
```
 
#### PubSubMessage
The syntax of these messages is the following
```
PubSubMessage msgName{
    properties
}
```

#### RPCMessage
These messages contain both the request and the response part
```
RPCMessage msgName{
    RPCRequest
    ---
    RPCResponse
}
```
where RPCRequest and RPCRequests are properties described above.

### MECO Definition


### Code Generation


### Documentation Generation


## Installation


## Examples