"""Tests for `str2bool` argparse converter.

`type=bool` is a footgun in argparse because `bool("False") is True`. The
converter exists so `--test False` actually means `False` in the batch
pipelines that previously used `type=bool`.
"""

import argparse
from unittest import TestCase

from cole.evaluation.tools import str2bool


class Str2BoolTest(TestCase):
    def test_truthy_strings(self):
        for value in ("True", "true", "TRUE", "1", "yes", "y", "t"):
            with self.subTest(value=value):
                self.assertTrue(str2bool(value))

    def test_falsy_strings(self):
        for value in ("False", "false", "FALSE", "0", "no", "n", "f"):
            with self.subTest(value=value):
                self.assertFalse(str2bool(value))

    def test_passes_actual_bools_through(self):
        self.assertTrue(str2bool(True))
        self.assertFalse(str2bool(False))

    def test_garbage_raises_argparse_error(self):
        # Crucially this is the case the old `type=bool` got wrong:
        # `bool("False")` returns True. Now we reject unknown spellings.
        with self.assertRaises(argparse.ArgumentTypeError):
            str2bool("maybe")
        with self.assertRaises(argparse.ArgumentTypeError):
            str2bool("")

    def test_integration_with_argparse(self):
        # Smoke test: an argparse parser using str2bool actually rejects
        # `--flag False` -> False (vs. the broken `type=bool` -> True).
        parser = argparse.ArgumentParser()
        parser.add_argument("--flag", type=str2bool, default=False)

        self.assertFalse(parser.parse_args(["--flag", "False"]).flag)
        self.assertTrue(parser.parse_args(["--flag", "True"]).flag)
        self.assertFalse(parser.parse_args([]).flag)
