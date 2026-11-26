import unittest

from cole.evaluation.tools import select_tasks
from cole.task.task_names import COLETasks


class TestSelectTasks(unittest.TestCase):
    group = [task.value for task in COLETasks]

    def test_none_or_blank_keeps_whole_group(self):
        self.assertEqual(self.group, select_tasks(self.group, None))
        self.assertEqual(self.group, select_tasks(self.group, "  "))

    def test_selection_is_trimmed_and_follows_group_order_without_duplicates(self):
        selected = select_tasks(self.group, "wsd, fquad,piaf,fquad")
        self.assertEqual(["fquad", "piaf", "wsd"], selected)

    def test_unknown_task_raises_with_its_name(self):
        with self.assertRaises(ValueError) as context:
            select_tasks(self.group, "fquad,not_a_task")
        self.assertIn("not_a_task", str(context.exception))

    def test_task_of_another_group_is_rejected(self):
        with self.assertRaises(ValueError):
            select_tasks(["frcoe"], "fquad")
