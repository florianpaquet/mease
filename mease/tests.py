import json
import unittest
from .registry import Mease
from .backends.test import TestBackend


class MeaseTestCase(unittest.TestCase):

    def setUp(self):
        self.mease = Mease(TestBackend, {})
        self.ret = type("", (), {})()

    def test_opener(self):
        """
        Tests openers callbacks
        """
        client = 'a'
        clients_list = ['d', 'e', 'f']

        # Register callback
        @self.mease.opener
        def opener_func(client, clients_list):
            self.ret.client = client
            self.ret.clients_list = clients_list

        # Register other callback
        @self.mease.opener
        def otjer_opener_func(client, clients_list):
            self.ret.other_client = client
            self.ret.other_clients_list = clients_list

        # Call openers
        self.mease.call_openers(client, clients_list)
        self.mease.executor.shutdown(wait=True)

        self.assertEqual(client, self.ret.client)
        self.assertListEqual(clients_list, self.ret.clients_list)

        self.assertEqual(client, self.ret.other_client)
        self.assertListEqual(clients_list, self.ret.other_clients_list)

    def test_closer(self):
        """
        Tests closers callbacks
        """
        client = 'a'
        clients_list = ['d', 'e', 'f']

        # Register callback
        @self.mease.closer
        def closer_func(client, clients_list):
            self.ret.client = client
            self.ret.clients_list = clients_list

        # Register other callback
        @self.mease.closer
        def other_closer_func(client, clients_list):
            self.ret.other_client = client
            self.ret.other_clients_list = clients_list

        # Call closers
        self.mease.call_closers(client, clients_list)
        self.mease.executor.shutdown(wait=True)

        self.assertEqual(client, self.ret.client)
        self.assertListEqual(clients_list, self.ret.clients_list)

        self.assertEqual(client, self.ret.other_client)
        self.assertListEqual(clients_list, self.ret.other_clients_list)

    def test_receiver(self):
        """
        Tests receivers callbacks
        """
        client = 'a'
        message = '{"message": "Hello world !"}'
        clients_list = ['d', 'e', 'f']

        # Register callback
        @self.mease.receiver(json=True)
        def json_receiver_func(client, clients_list, message):
            self.ret.json_client = client
            self.ret.json_message = message
            self.ret.json_clients_list = clients_list

        # Register callback
        @self.mease.receiver
        def raw_receiver_func(client, clients_list, message):
            self.ret.raw_client = client
            self.ret.raw_message = message
            self.ret.raw_clients_list = clients_list

        # Call receivers
        self.mease.call_receivers(client, clients_list, message)
        self.mease.executor.shutdown(wait=True)

        json_message = json.loads(message)
        self.assertEqual(client, self.ret.json_client)
        self.assertEqual(json_message, self.ret.json_message)
        self.assertListEqual(clients_list, self.ret.json_clients_list)

        self.assertEqual(client, self.ret.raw_client)
        self.assertEqual(message, self.ret.raw_message)
        self.assertListEqual(clients_list, self.ret.raw_clients_list)

    def test_sender(self):
        """
        Tests senders callbacks
        """
        message = "Hello world !"
        routing = 'mease.test'

        # Register callback
        @self.mease.sender(routing='mease.test')
        def sender_func(routing, message):
            self.ret.routing = routing
            self.ret.message = message

        # This callback will not be called
        @self.mease.sender(routing='mease.other')
        def other_sender_func(routing, message):
            self.ret.other_routing = routing
            self.ret.other_message = message

        # Call senders
        self.mease.call_senders(routing, message)
        self.mease.executor.shutdown(wait=True)

        self.assertEqual(routing, self.ret.routing)
        self.assertEqual(message, self.ret.message)

        self.assertFalse(hasattr(self.ret, 'other_routing'))
        self.assertFalse(hasattr(self.ret, 'other_message'))


if __name__ == '__main__':
    unittest.main()
