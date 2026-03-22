from typing import Callable, Dict
from unittest import TestCase

import pytest
from fastapi import HTTPException

from src.backend.validation_tools import (
    validate_submission_tasks_name,
    validate_submission_json,
    validate_submission_template,
)


class ValidateTest(TestCase):
    @staticmethod
    def assertNotRaises(method: Callable, **kwargs: Dict) -> None:
        try:
            method(**kwargs)
        except HTTPException as e:
            pytest.fail(e.args[0])

    def setUp(self) -> None:
        a_prediction_list = [1, 1, 1, 1, 1]
        self.a_submission_json = {
            "model_name": "a_model_name",
            "model_url": "a_model_url",
            "tasks": [
                {"qfrcola": {"predictions": a_prediction_list}},
                {"allocine": {"predictions": a_prediction_list}},
            ],
        }

        self.a_missing_model_name_submission_json = {
            "model_url": "a_model_url",
            "tasks": [
                {"qfrcola": {"predictions": a_prediction_list}},
                {"allocine": {"predictions": a_prediction_list}},
            ],
        }

        self.a_missing_model_url_submission_json = {
            "model_name": "a_model_name",
            "tasks": [
                {"qfrcola": {"predictions": a_prediction_list}},
                {"allocine": {"predictions": a_prediction_list}},
            ],
        }

        self.a_missing_task_submission_json = {
            "model_name": "a_model_name",
            "model_url": "a_model_url",
        }

        self.a_missing_task_content_submission_content = {
            "model_name": "a_model_name",
            "model_url": "a_model_url",
            "tasks": "missing",
        }

        self.a_two_task_dict_in_list = {
            "model_name": "a_model_name",
            "model_url": "a_model_url",
            "tasks": [
                {
                    "qfrcola": {"predictions": a_prediction_list},
                    "allocine": {"predictions": a_prediction_list},
                },
            ],
        }

        self.a_wrong_task_name = {
            "model_name": "a_model_name",
            "model_url": "a_model_url",
            "tasks": [
                {"wrong_task_name": {"predictions": a_prediction_list}},
                {"allocine": {"predictions": a_prediction_list}},
            ],
        }

        self.unaccepted_task_dict_not_dict = {
            "model_name": "a_model_name",
            "model_url": "a_model_url",
            "tasks": [
                {"qfrcola": "not a dict"},
                {"allocine": {"predictions": a_prediction_list}},
            ],
        }

        self.unaccepted_task_dict_no_prediction = {
            "model_name": "a_model_name",
            "model_url": "a_model_url",
            "tasks": [
                {"qfrcola": {"unaccepted_field": a_prediction_list}},
                {"allocine": {"predictions": a_prediction_list}},
            ],
        }

        self.unaccepted_task_dict_prediction_not_list = {
            "model_name": "a_model_name",
            "model_url": "a_model_url",
            "tasks": [
                {"qfrcola": {"predictions": a_prediction_list}},
                {"allocine": {"predictions": "not_list"}},
            ],
        }


class ValidateSubmissionFormat(ValidateTest):

    def test_given_an_acceptable_format_then_does_not_raise_error(self):
        self.assertNotRaises(
            validate_submission_template, **{"dictionary": self.a_submission_json}
        )

    def test_given_a_missing_model_name_raise_error(self):
        self.assertRaises(
            HTTPException,
            validate_submission_template,
            **{"dictionary": self.a_missing_model_name_submission_json}
        )

    def test_given_a_missing_model_url_raise_error(self):
        self.assertRaises(
            HTTPException,
            validate_submission_template,
            **{"dictionary": self.a_missing_model_url_submission_json}
        )

    def test_given_a_missing_task_raise_error(self):
        self.assertRaises(
            HTTPException,
            validate_submission_template,
            **{"dictionary": self.a_missing_task_submission_json}
        )

    def test_given_a_missing_task_content_raise_error(self):
        self.assertRaises(
            HTTPException,
            validate_submission_template,
            **{"dictionary": self.a_missing_task_content_submission_content}
        )

    def test_given_a_two_task_content_raise_error(self):
        self.assertRaises(
            HTTPException,
            validate_submission_template,
            **{"dictionary": self.a_two_task_dict_in_list}
        )


class ValidateSubmissionTasksNameJSONTest(ValidateTest):
    def test_given_a_json_of_accepted_task_when_validate_then_does_not_raise_error(
        self,
    ):
        self.assertNotRaises(
            validate_submission_tasks_name, **{"dictionary": self.a_submission_json}
        )

    def test_given_a_json_of_unaccepted_task_when_validate_then_does_raise_error(self):

        self.assertRaises(
            HTTPException,
            validate_submission_tasks_name,
            **{"dictionary": self.a_wrong_task_name}
        )


class ValidateSubmissionJSONTest(ValidateTest):
    def test_given_a_json_of_accepted_format_when_validate_then_does_not_raise_error(
        self,
    ):
        self.assertNotRaises(
            validate_submission_tasks_name, **{"dictionary": self.a_submission_json}
        )

    def test_given_a_json_of_unaccepted_format_when_validate_then_does_raise_error(
        self,
    ):
        self.assertRaises(
            HTTPException,
            validate_submission_json,
            **{"dictionary": self.unaccepted_task_dict_not_dict}
        )

        self.assertRaises(
            HTTPException,
            validate_submission_json,
            **{"dictionary": self.unaccepted_task_dict_no_prediction}
        )

        self.assertRaises(
            HTTPException,
            validate_submission_json,
            **{"dictionary": self.unaccepted_task_dict_prediction_not_list}
        )
