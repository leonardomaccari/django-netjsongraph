from django.test import TestCase

from ..models import Topology


class TestRestFramework(TestCase):
    fixtures = [
        'test_nodes.json'
    ]

    def test_list(self):
        response = self.client.get('/api/topology/')
        self.assertEqual(response.data['type'], 'NetworkCollection')
        self.assertEqual(len(response.data['collection']), 1)

    def test_detail(self):
        response = self.client.get('/api/topology/0b876cac-1a94-49fa-b90a-8c0df1039a4d/')
        self.assertEqual(response.data['type'], 'NetworkGraph')
