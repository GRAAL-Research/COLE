from typing import List
from unittest import TestCase

from src.task.task_factory import tasks_factory
from src.backend.validation_tools import tasks_name


class TasksFactoryTest(TestCase):
    def test_task_factory(self):
        a_prediction_list = [1, 1, 1, 1, 1]
        tasks_payload = [
            {task: {"predictions": a_prediction_list}} for task in tasks_name
        ]
        a_submission_json = {
            "model_name": "a_model_name",
            "model_url": "a_model_url",
            "tasks": tasks_payload,
        }

        actual_tasks_list = tasks_factory(a_submission_json)

        self.assertIsInstance(actual_tasks_list, List)

        expected_len = len(tasks_name)
        actual_len = len(actual_tasks_list)
        self.assertEqual(expected_len, actual_len)

    def test_task_factory_raise_error_name_not_valid(self):
        a_prediction_list = [1, 1, 1, 1, 1]
        tasks_payload = [
            {task: {"predictions": a_prediction_list}} for task in ["invalid name"]
        ]
        a_submission_json = {
            "model_name": "a_model_name",
            "model_url": "a_model_url",
            "tasks": tasks_payload,
        }

        self.assertRaises(ValueError, tasks_factory, a_submission_json)
