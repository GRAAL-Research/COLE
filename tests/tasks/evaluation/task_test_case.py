from typing import Dict
from unittest import TestCase


class TaskTest(TestCase):
    def assertEvalDictEqual(self, dict1: Dict, dict2: Dict) -> None:
        for (key_1, value_1), (key_2, value_2) in zip(dict1.items(), dict2.items()):
            self.assertEqual(key_1, key_2)
            self.assertAlmostEqual(value_1, value_2, delta=0.1)
