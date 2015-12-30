from django.test import TestCase, override_settings

from ..models import Update
from django.conf import settings


class TestUpdate(TestCase):
    fixtures = [
        'test_nodes.json'
    ]

    def test_add_single(self):
        u = Update()
        u.save()
        new_u = Update.objects.last()
        self.assertEqual(new_u.id, 57)

    def test_multiple_updates(self):
        for i in range(5):
            u = Update()
            u.save()
        self.assertEqual(len(Update.objects.all()), 6)
