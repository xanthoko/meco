## TO-DO Checklist

- [x] Create Basic Grammar
- [x] Parse Model
- [x] Create commlib entities
- [x] Connect commlib entities via connector
- [x] Create a test environment
- [x] Add dataModel to Ports
- [x] Allow more than one service instace per service type in nodes (e.g. 2 publishers in a node)
- [ ] Make a test case with a real sensor and arduino
- [ ] Integrate RPC communications
- [ ] Add support for redis and mqtt protocol


## Example

The example contains a dummy model of a *thermoSensor* node with a publisher
and an *ACDevice* with a subscriber that are connected via a connector.

To run the example you have to open a rabbitmq server in localhost by running `rabbitmq-server`.
Then inside the nodem directory, run `python example.py sub` to fire up the subscriber.

On another terminal, in the same directory run `python -i example.py pub`. This intercative shell will have a publisher called **example_publisher** and you will be able to test their connection by executing `example_publisher.publish()`.

Now on the first terminal you can see the message sent by the publisher.
