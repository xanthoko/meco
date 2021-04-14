## TO-DO Checklist

- [x] Create Basic Grammar
- [x] Parse Model
- [x] Create commlib entities
- [x] Add dataModel to Ports
- [x] Allow more than one service instace per service type in nodes (e.g. 2 publishers in a node)
- [x] Introduce topic field in services
- [x] Implement comm-idl pubsub_message handling
- [x] Implement comm-idl rpc_message handling
- [x] Replace objects with idl-objects
- [x] Create package
- [x] Integrate RPC communications
- [x] Override commlib generator for on_request methods
- [x] Integrate broker-dsl
- [x] Add support for redis and mqtt protocol
- [x] Specify broker for every node
- [ ] Create a bridge to bind brokers

## Examples

The example model consists of 4 Nodes, each representing a part of a smart home system. The nodes have outports and inports that connect them with each other. To run the example open two terminals in the *examples* directory.


### Starting the broker
Nodem supports 3 broker communication protocols.
* AMQP
* MQTT
* Redis

You can declare the connection parameters of the broker of your choise in *broker.dsl*. To start them in localhost you can use:
* rabbitmq-server
* docker run -d --name emqx -p 1883:1883 -p 8083:8083 -p 8883:8883 -p 8084:8084 -p 18083:18083 emqx/emqx:4.2.8
* redis-server


### Pub-Sub Example
Run `python ps_example.py sub` to fire up the subscriber.
On another terminal, in the same directory run `python ps_example.py pub`. This command will create a publisher that publishes an example message with the same topic as the subscriber.

On the first terminal, there will be the message sent by the publisher.


### RPC Example
Run `python rpc_example.py service` to fire up the rpc service.
On another terminal, in the same directory run `python rpc_example.py client`. This command will create an rpc client called **example_rpc_client** that sends a message. The message is specifed in the **messages.idl** file.

Now on the first terminal you can see the message sent by the client.
