from http.client import HTTPException
from unittest import TestCase

from src.backend.submit_tools import (
    convert_custom_dict_to_task_dict,
    get_max_samples,
    get_tasks_as_str,
)


class ConvertCustomDictToTaskDictTest(TestCase):
    def setUp(self):
        self.task = "qfrcola"

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


class GetMaxSamplesTest(TestCase):
    def test_given_a_dictionary_of_five_element_when_get_max_samples_then_return_five(
        self,
    ):
        a_list_five_elements = [1] * 5

        a_dictionary_five_elements = {f"TASK": a_list_five_elements}

        expected = 5

        actual = get_max_samples(tasks_prediction_dictionary=a_dictionary_five_elements)

        self.assertEqual(expected, actual)


class GetTasksAsStr(TestCase):
    def setUp(self):
        self.a_list = []

    def test_given_a_single_dict_task_when_get_tasks_as_str_then_return_tasks_as_str(
        self,
    ):
        a_fr_cola_dict = {"qfrcola": self.a_list}

        expected = "custom|qfrcola|0|0"

        actual, _ = get_tasks_as_str(tasks_prediction_dictionary=a_fr_cola_dict)

        self.assertEqual(expected, actual)

        a_fr_cola_dict = {"allocine": self.a_list}

        expected = "custom|allocine|0|0"

        actual, _ = get_tasks_as_str(tasks_prediction_dictionary=a_fr_cola_dict)

        self.assertEqual(expected, actual)

    def test_given_a_double_dict_task_when_get_tasks_as_str_then_return_tasks_as_str(
        self,
    ):
        a_dict = {"qfrcola": self.a_list, "allocine": self.a_list}

        expected = "custom|allocine|0|0,custom|qfrcola|0|0"

        actual, _ = get_tasks_as_str(tasks_prediction_dictionary=a_dict)

        self.assertEqual(expected, actual)

    def test_given_a_single_dict_task_when_get_tasks_as_str_then_return_available_tasks(
        self,
    ):
        a_fr_cola_dict = {"qfrcola": self.a_list}

        expected = ["qfrcola"]

        _, actual = get_tasks_as_str(tasks_prediction_dictionary=a_fr_cola_dict)

        self.assertEqual(expected, actual)

        a_fr_cola_dict = {"allocine": self.a_list}

        expected = ["allocine"]

        _, actual = get_tasks_as_str(tasks_prediction_dictionary=a_fr_cola_dict)

        self.assertEqual(expected, actual)

    def test_given_a_empty_dict_task_when_get_tasks_as_str_then_raiseException(self):
        an_empty_dict = {}

        self.assertRaises(
            HTTPException,
            get_tasks_as_str,
            tasks_prediction_dictionary=an_empty_dict,
        )
