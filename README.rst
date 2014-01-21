#####
mease
#####

.. image:: https://travis-ci.org/florianpaquet/mease.png?branch=master

Websocket server using Tornado with an easy to use callback registry mechanism

See `django-mease <https://github.com/florianpaquet/django-mease>`_, `django-mease-example <https://github.com/florianpaquet/django-mease-example>`_ or `flask-mease-example <https://github.com/florianpaquet/flask-mease-example>`_ for working examples.

************
Installation
************

Use pip to install the latest mease version : ::

    pip install mease

``mease`` comes with two backends :

Redis
=====

To use Redis backend, install these dependencies : ::

    sudo apt-get install redis-server
    pip install redis toredis-mease

Refer to the `Redis documentation <http://redis.io/documentation>`_ to configure your server.

RabbitMQ
========

To use RabbitMQ backend, install these dependencies : ::

    sudo apt-get install rabbitmq-server
    pip install pika

Refer to the `RabbitMQ documentation <http://www.rabbitmq.com/documentation.html>`_ to configure your server.

**********
Quickstart
**********

Create a mease registry file where you create your callbacks and register them :

.. code:: python

    from mease import Mease
    from mease.backends.redis import RedisBackend
    # OR from mease.backends.rabbitmq import RabbitMQBackend

    mease = Mease(RedisBackend)

    @mease.opener
    def example_opener(client, clients_list):
        # Do stuff on client connection
        pass

    @mease.closer
    def example_closer(client, clients_list):
        # Do stuff on client disconnection
        pass

    @mease.receiver(json=True)
    def example_receiver(client, clients_list, message):
        # Do stuff on incoming client message
        pass

    @mease.sender(routing='mease.demo')
    def example_sender(routing, clients_list, my_tuple):
        # Do stuff on outgoing message
        pass

    if __name__ == '__main__':
        # Start websocket server
        mease.run_websocket_server()

In your code, you can now call the mease ``publish`` method to send a message to websocket clients :

.. code:: python

    from mease import Mease
    from mease.backends.redis import RedisBackend
    
    mease = Mease(RedisBackend)
    
    # ...
    
    mease.publish('mease.demo', my_tuple=("Hello", "World"))
    
That's it ! You are now able to send messages from your web server to your websocket server in a cool way !