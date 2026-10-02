import unittest
from review import review_text


class WorkflowTests(unittest.TestCase):
    def test_implicit_and_privileged_trigger(self):
        rules = {x["rule"] for x in review_text("on: pull_request_target\njobs:\n  test:\n    runs-on: ubuntu-latest\n")}
        self.assertEqual(rules, {"privileged-pr-trigger", "implicit-token-permissions"})

    def test_explicit_scoped_permissions(self):
        self.assertEqual(review_text("on: push\npermissions:\n  contents: read\njobs:\n  test:\n    runs-on: ubuntu-latest\n"), [])

    def test_write_and_bad_shape(self):
        self.assertEqual(review_text("permissions: write-all\njobs: {test: {}}")[-1]["rule"], "write-all")
        for value in ("[]", "jobs: []", "jobs: {test: []}"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                review_text(value)
