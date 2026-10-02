import json
import plistlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from review import review_text


class RegressionTests(unittest.TestCase):

    def test_bad_trigger_permissions_and_duplicate_keys(self):
        for text in ("on: [{}]\npermissions: {}\njobs: {test: {}}", "on: push\npermissions: {contents: []}\njobs: {test: {}}", "on: push\npermissions: write-all\npermissions: {}\njobs: {test: {}}"):
            with self.subTest(text=text), self.assertRaises(ValueError): review_text(text)
    def test_job_permissions_without_root_defaults(self):
        self.assertEqual(review_text("on: push\njobs:\n  test:\n    permissions: {contents: read}\n"),[])
