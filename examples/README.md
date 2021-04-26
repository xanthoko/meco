## Examples

There are 3 example cases each with its own model. To run them open up a terminal and a broker. 

### Starting the broker
Nodem supports 3 broker communication protocols.
* AMQP
* MQTT
* Redis

You can declare the connection parameters of the brokers you choose in *broker.dsl*. 
To start them in locally use the following commands:
* **RABBITMQ**: rabbitmq-server
* **REDIS**: redis-server
* **EMQX**: docker run -it --rm --name emqx -p 18083:18083 -p 1883:1883 emqx/emqx:latest


### Example #1  (Simple nodes)
This example has one OutNode with a publisher and an rpc services and one InNode with a subscriber and an rpc client. The publisher is connected with the subscriber via the same topic and the rpc endpoints via the same name.

To check the connections you can fire up a terminal and run `python -i simple.py`. You can either run `example_publisher.publish()` or `example_rpc_client.call(request)` to test that the endpoints are valid.


### Example #2  (Brigde)
Again, there is one OutNode and one InNode but their endpoints are not connected to each other and are in different brokers. 

To connect them we use a TopicBride and an RPCBridge.

To check that the endpoints are connected run `python -i bridge.py` and then either `example_publisher.publish()` or `example_rpc_client.call(request)`. If you comment out the brige lines (27,35) you can verify that the messages are not arriving in the InNode.


### Example #3  (Proxy)
In this example, there is an OutNode with a publisher *(external_publisher)* and an InNode with a subscriber *(external_subscriber)*.

There is also a proxy that when its subscriber consumes an event, it makes a request to "localhost:8000" and publishes the response to the external_subscriber.

Open a terminal and run `python -i proxy.py`. To trigger the proxy functionality execute `external_publisher.publish()` and see the external_subscriber consume the response from "localhost:8000"