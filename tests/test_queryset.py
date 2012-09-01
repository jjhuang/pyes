#!/usr/bin/env python
# -*- coding: utf-8 -*-

from estestcase import ESTestCase
import unittest
from pyes.queryset import ESModel, QuerySet, DoesNotExist, generate_model


class QuerySetTests(ESTestCase):
    def setUp(self):
        super(QuerySetTests, self).setUp()
        self.init_default_index()
        self.init_default_data()
        self.conn.refresh(self.index_name)

    def init_default_data(self):
        """
        Init default index data
        """
        self.conn.index({"name": ["Joe Tester", "J. Tester"], "parsedtext": "Joe Testere nice guy", "uuid": "11111",
                         "position": 1},
            self.index_name, self.document_type, 1)
        self.conn.index({"name": "data1", "value": "value1"}, self.index_name, "test-type2", 1, parent=1)
        self.conn.index({"name": "Bill Baloney", "parsedtext": "Bill Testere nice guy", "uuid": "22222", "position": 2},
            self.index_name, self.document_type, 2)
        self.conn.index({"name": "data2", "value": "value2"}, self.index_name, "test-type2", 2, parent=2)
        self.conn.index({"name": ["Bill Clinton", "B. Clinton"], "parsedtext": """Bill is not
                nice guy""", "uuid": "33333", "position": 3}, self.index_name, self.document_type, 3)

    def test_get(self):
        model = generate_model(self.index_name, self.document_type)
        queryset = model.objects
        self.assertEqual(len(queryset), 3)
        queryset = model.objects.all()
        self.assertEqual(len(queryset), 3)
        queryset = model.objects.filter(uuid="33333")
        self.assertEqual(len(queryset), 1)
        queryset = model.objects.filter(position=1)
        self.assertEqual(len(queryset), 1)
        queryset = model.objects.filter(position=1).filter(position=3)
        self.assertEqual(len(queryset), 0)
        queryset = model.objects.filter(uuid="33333", position=3)
        self.assertEqual(len(queryset), 1)
        queryset = model.objects.filter(position__gt=1, position__lt=3)
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual([r.position for r in queryset], [2])
        queryset = model.objects.exclude(position=1)
        self.assertEqual(len(queryset), 2)
        self.assertEqual(queryset.count(), 2)
        self.assertEqual([r.position for r in queryset], [2,3])
        queryset = model.objects.exclude(position__in=[1,2])
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual([r.position for r in queryset], [3])

        item = model.objects.get(position=1)
        self.assertEqual(item.position, 1)
        self.assertRaises(DoesNotExist, model.objects.get, position=0)

        queryset = model.objects.order_by("position")
        self.assertEqual(queryset[0].position, 1)
        queryset = model.objects.order_by("-position")
        self.assertEqual(queryset[0].position, 3)


        item, created = model.objects.get_or_create(position=1, defaults={"name":"nasty"})
        self.assertEqual(created, False)
        self.assertEqual(item.position, 1)
        self.assertEqual(item.get_meta().id, "1")
        item, created = model.objects.get_or_create(position=10, defaults={"name":"nasty"})
        self.assertEqual(created, True)
        self.assertEqual(item.position, 10)
