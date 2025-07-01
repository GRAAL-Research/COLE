from unittest import TestCase

from src.backend.submit_tools import convert_custom_dict_to_task_dict


class ConvertCustomDictToTaskDictTest(TestCase):
    def setUp(self):
        self.task = "frcola"

    def test_given_proper_dictionary_when_get_convert_custom_dict_to_task_dict_then_return_convert(
        self,
    ):
        a_list = []

        a_dictionary = {f"custom|{self.task}|0|0": a_list}

        expected = {self.task: a_list}

        actual = convert_custom_dict_to_task_dict(dictionary=a_dictionary)

        self.assertEqual(expected, actual)

    def test_given_a_dictionary_with_missing_custom_tag_when_convert_custom_dict_to_task_dict_then_raise_ValueError(
        self,
    ):
        a_list = []

        a_dictionary_missing_custom_tag = {f"|{self.task}|0|0": a_list}

        self.assertRaises(
            ValueError,
            convert_custom_dict_to_task_dict,
            dictionary=a_dictionary_missing_custom_tag,
        )

    def test_given_a_dictionary_with_missing_straight_bar_tag_when_convert_custom_dict_to_task_dict_then_raise_ValueError(
        self,
    ):
        a_list = []

        a_dictionary_missing_a_straight_bar_tag = {f"custom{self.task}|0|0": a_list}

        self.assertRaises(
            ValueError,
            convert_custom_dict_to_task_dict,
            dictionary=a_dictionary_missing_a_straight_bar_tag,
        )
