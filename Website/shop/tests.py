from django.test import TestCase

from .models import *


class shop_category_test(TestCase):

    def setUp(cls):
        cls.cat = Category.objects.create(name='testcat', slug='testcatslug')

    def test_cat_name(self):
        self.assertIsInstance(self.cat.name, str)

    def test_cat_slug(self):
        self.assertIsInstance(self.cat.slug, str)
