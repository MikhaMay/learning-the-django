from django.test import TestCase

from store.logic import operations



class LogicTestCase(TestCase):
    def test_plus(self):
        result = operations(6, 13, '+')
        self.assertEqual(19, result)

    def test_minus(self):
        result = operations(10, 10, '-')
        self.assertEqual(0, result)
    
    def test_minus2(self):
        result = operations(10, 9, '-')
        self.assertEqual(1, result)
    
    def test_multiply(self):
        result = operations(10, 9, '*')
        self.assertEqual(90, result)

