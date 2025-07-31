import unittest

from predictions.all_llms import llms
from src.evaluation.tools import split_llm_list


class TestTools(unittest.TestCase):

    def setUp(self):
        self.llms = llms["all"]

    def test_given_a_list_of_llm_when_all_split_then_equal_original_list(self):
        split_1 = split_llm_list(models=self.llms, llm_split=1)
        split_2 = split_llm_list(models=self.llms, llm_split=2)
        split_3 = split_llm_list(models=self.llms, llm_split=3)

        expected = self.llms
        actual = split_1 + split_2 + split_3
        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_given_a_list_of_llm_when_split_none_then_equal_original_list(self):
        actual = split_llm_list(models=self.llms, llm_split=None)

        expected = self.llms

        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)
