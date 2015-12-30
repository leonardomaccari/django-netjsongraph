import six
from django.test import TestCase
from django.core.exceptions import ValidationError

from ..models import Link, Node, Topology, Update


class TestLink(TestCase):
    """
    tests for Link model
    """
    fixtures = [
        'test_nodes.json'
    ]

    def test_str(self):
        l = Link(topology_id="0b876cac-1a94-49fa-b90a-8c0df1039a4d",
                 source_id="ba19f510-18e3-40e5-abb7-67de305e6655",
                 target_id="5588138d-9f4f-4aef-8a95-64c844456de3",
                 update_id=56,
                 cost=1.0)
        self.assertIsInstance(str(l), str)

    def test_clean_properties(self):
        l = Link(topology_id="0b876cac-1a94-49fa-b90a-8c0df1039a4d",
                 source_id="ba19f510-18e3-40e5-abb7-67de305e6655",
                 target_id="5588138d-9f4f-4aef-8a95-64c844456de3",
                 cost=1.0,
                 update_id=56,
                 properties=None)
        l.full_clean()
        self.assertEqual(l.properties, {})

    def test_same_source_and_target_id(self):
        l = Link(topology_id="0b876cac-1a94-49fa-b90a-8c0df1039a4d",
                 source_id="ba19f510-18e3-40e5-abb7-67de305e6655",
                 target_id="ba19f510-18e3-40e5-abb7-67de305e6655",
                 update_id=56,
                 cost=1)
        with self.assertRaises(ValidationError):
            l.full_clean()

    def test_same_source_and_target(self):
        node = Node.objects.first()
        l = Link(topology=Topology.objects.first(),
                 source=node,
                 target=node,
                 update=Update.objects.last(),
                 cost=1)
        with self.assertRaises(ValidationError):
            l.full_clean()

    def test_json(self):
        self.maxDiff = None
        l = Link(topology_id="0b876cac-1a94-49fa-b90a-8c0df1039a4d",
                 source_id="ba19f510-18e3-40e5-abb7-67de305e6655",
                 target_id="5588138d-9f4f-4aef-8a95-64c844456de3",
                 cost=1.0,
                 cost_text='100mbit/s',
                 update_id=56,
                 properties='{"pretty": true}')
        self.assertEqual(dict(l.json(dict=True)), {
            'source': '192.168.0.1',
            'target': '192.168.0.2',
            'cost': 1.0,
            'cost_text': '100mbit/s',
            'properties': {
                'pretty': True,
                'status': 'up',
                'created': l.created,
                'modified': l.modified
            }
        })
        self.assertIsInstance(l.json(), six.string_types)

    def test_get_from_nodes(self):
        l = Link(topology_id="0b876cac-1a94-49fa-b90a-8c0df1039a4d",
                 source_id="ba19f510-18e3-40e5-abb7-67de305e6655",
                 target_id="5588138d-9f4f-4aef-8a95-64c844456de3",
                 cost=1.0,
                 cost_text='100mbit/s',
                 update_id=56,
                 properties='{"pretty": true}')
        l.full_clean()
        l.save()
        l = Link.get_from_nodes('192.168.0.1', '192.168.0.2')
        self.assertIsInstance(l, Link)
        l = Link.get_from_nodes('wrong', 'wrong')
        self.assertIsNone(l)
