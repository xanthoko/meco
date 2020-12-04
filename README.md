## TO-DO Checklist

- [x] Create Basic Grammar
- [x] Parse Model
- [x] Create commlib entities
- [x] Connect commlib entities via connector
- [ ] Create a test environment
- [ ] Add dataModel to Ports
- [ ] Test Publishers
- [ ] Integrate RPC communications

## Example

The example contains a dummy model of a *thermoSensor* node with a publisher
and an *ACDevice* with a subscriber that are connected via a connector.

To run the example in a terminal run `python parser.py test sub` to run the subscriber.

On another terminal run `python -i parser.py test pub`. This intercative shell will have a publisher called **test_publisher** and you will be able to test their connection by executing `test_publisher.publish()`.

On the first shell will be printed the message sent by the publisher.
