## Examples

There are 3 example cases each with its own MECO model and shared broker and messages models.

**NOTE**: All the executions of the generated python files must be made with the -i flag, to keep the interactive shell open.

### Starting the broker
MECO supports 3 broker communication protocols.
* AMQP
* MQTT
* Redis

You can declare the connection parameters of the brokers you choose in *brokers.br*. 
To start them locally use the following commands:
* **RABBITMQ**: rabbitmq-server
* **REDIS**: redis-server
* **EMQX**: docker run -it --rm --name emqx -p 18083:18083 -p 1883:1883 emqx/emqx:latest


### Example #1  (Simple nodes)
This example has one Node with a publisher and an rpc services and one Node with a subscriber and an rpc client. The publisher is connected with the subscriber via the same topic and the rpc endpoints via the same name.

To generate the code files, go inside the meco directory and run 
``` $ python parser.py --model ../examples/simple.ent --messages ../examples/messages.idl```

Then you can either add `publisher_1.publish_with_freq()` or `rpc_client_1.call_with_freq()` in node_thermoSensor.py and comment in the `node.run_subscribers()`
or `node.run_rpcs()` lines in node_ACDevice.py file in the **code_outputs** directory to test the functionality of the endpoints.

First, execute
```$ python -i node_ACDevices.py``` 
and then in another terminal
```$ python -i node_thermoSensor.py```.
You will see in the first terminal the messages consumed either by the subscriber or the rpc_service.

To generate the documentation for this example run `python doc_parser.py --model ../examples/simple.ent`


### Example #2  (Brigde)
Again, there are two nodes but their endpoints are not connected to each other and are in different brokers. To connect them we use a TopicBride and an RPCBridge.

To generate the code files, go inside the meco directory and run
```$ python parser.py --model ../examples/bridge.ent --messages ../examples/messages.idl```

Then you can either add `publisher_1.publish_with_freq()` or `rpc_client_1.call_with_freq()` in node_thermoSensor.py and comment in the `node.run_subscribers()`
or `node.run_rpcs()` lines in node_ACDevice.py file in the **code_outputs** directory to test the functionality of the endpoints.

Because the ACDevice node is connected to a local redis, you have to execute `redis-server` in a terminal to fire up the redis broker.

First, execute
```$ python -i node_ACDevices.py``` and then in another terminal
```$ python -i node_thermoSensor.py```.
The messages will not be consumed until you execute `python -i tbridge_R4A2Redis.py` or `python -i rbridge_R4A2Redis.py` to activate the connecting bridges.

To generate the documentation for this example run
```$ python doc_parser.py --model ../examples/bridge.ent```


### Example #3  (Proxy)
In this example, there is an Node with an rpc_client and a RESTProxy with an rpc_service. The two rpc endpoints are connected via the same name. The proxy makes a simple get request to Google's home page.

To generate the code files, go inside the meco directory and run
```$ python parser.py --model ../examples/proxy.ent --messages ../examples/messages.idl```

Then you can add `rpc_client_1.call()` in node_thermoSensor.py.
To check the functionality of the rest proxy, first execute
```$ python -i proxy_testProxy.py``` and in another terminal
```$ python -i node_thermoSensor.py```.

To generate the documentation for this example run 
```$ python doc_parser.py --model ../examples/proxy.ent```