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
- [ ] Integrate broker-dsl
- [ ] Add support for redis and mqtt protocol


## Examples

The example contains a dummy model of a *thermoSensor* node with a publisher
and an *ACDevice* with a subscriber that are connected via a connector.

To run any example you have to open a rabbitmq server in localhost by running `rabbitmq-server` and navigate to the examples directory.


### Pub-Sub Example
Run `python ps_example.py sub` to fire up the subscriber.
On another terminal, in the same directory run `python ps_example.py pub`. This command will create a publisher that publishes an example message with the same topic as the subscriber.

On the first terminal, there will be the message sent by the publisher.


### RPC Example
Run `python rpc_example.py service` to fire up the rpc service.
On another terminal, in the same directory run `python rpc_example.py client`. This command will create an rpc client called **example_rpc_client** that sends a message. The message is specifed in the **messages.idl** file.

Now on the first terminal you can see the message sent by the client.
