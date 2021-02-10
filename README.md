## TO-DO Checklist

- [x] Create Basic Grammar
- [x] Parse Model
- [x] Create commlib entities
- [x] Connect commlib entities via connector
- [x] Create a test environment
- [x] Add dataModel to Ports
- [x] Allow more than one service instace per service type in nodes (e.g. 2 publishers in a node)
- [x] Introduce topic field in services
- [ ] Replace objects with idl-objects
- [ ] Create package
- [x] Integrate RPC communications
- [ ] Add support for redis and mqtt protocol


## Examples

The example contains a dummy model of a *thermoSensor* node with a publisher
and an *ACDevice* with a subscriber that are connected via a connector.

To run any example you have to open a rabbitmq server in localhost by running `rabbitmq-server` and navigate to the examples directory.


### Pub-Sub Example
Run `python ps_example.py sub` to fire up the subscriber.
On another terminal, in the same directory run `python -i ps_example.py pub`. This intercative shell will have a publisher called **example_publisher** and you will be able to test their connection by executing `example_publisher.publish()`.

Now on the first terminal you can see the message sent by the publisher.


### RPC Example
Run `python rpc_example.py service` to fire up the rpc service.
On another terminal, in the same directory run `python -i ps_example.py client`. This intercative shell will have an rpc client called **example_rpc_client** and message to send. You will be able to test their connection by executing `example_rpc_client.call(msg)`.

Now on the first terminal you can see the message sent by the client.
