import unittest

from evergreen_lint import rules
from evergreen_lint.yamlhandler import load


class TestTasksForVariant(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = rules.tasks_for_variants.TasksForVariants()
        self.good_config = {
            "task-variant-mappings": [
                {"name": "mapping1", "tasks": ["t1", "t2"], "variants": ["v1", "v2"]},
                {"name": "mapping2", "tasks": ["t1", "t2", "t3"], "variants": ["v3"]},
                {"name": "mapping3", "tasks": ["t4"], "variants": ["v4"]},
            ]
        }

        self.good_yaml = load(
            """
    buildvariants:
    - name: v1
      tasks:
      - name: t1
      - name: t2
    - name: v2
      tasks:
      - name: t1
      - name: t2
    - name: v3
      tasks:
      - name: t1
      - name: t2
      - name: t3
    - name: v4
      tasks:
      - name: t4
    - name: v_dupe
      tasks:
      - name: t3
            """
        )

    def test_dupe_variant_in_config(self):
        dupe_variant_config = {
            "task-variant-mappings": [
                {"name": "mapping1", "tasks": ["t1", "t2"], "variants": ["v_dupe", "v2"]},
                {"name": "mapping2", "tasks": ["t3"], "variants": ["v_dupe"]},
            ]
        }

        violations = self.rule(dupe_variant_config, self.good_yaml)
        self.assertEqual(len(violations), 1)
        self.assertIn("more than once", violations[0])

    def test_unknown_variant_in_config(self):
        typo_variant_config = {
            "task-variant-mappings": [
                {"name": "mapping1", "tasks": ["t1", "t2"], "variants": ["v1", "v2"]},
                {"name": "mapping2", "tasks": ["t1", "t2", "t3"], "variants": ["v_typo"]},
            ]
        }

        violations = self.rule(typo_variant_config, self.good_yaml)
        self.assertEqual(len(violations), 1)
        self.assertIn("unknown variant", violations[0])

    def test_conforming_tasks(self):
        violations = self.rule(self.good_config, self.good_yaml)
        self.assertEqual(violations, [])

    def test_mismatched_tasks(self):
        bad_yaml = load(
            """
    buildvariants:
    - name: v1
      tasks:
      - name: t1
      - name: t2
    - name: v2
      tasks:
      - name: t1
      - name: t2
      - name: t3  # Extra task.
    - name: v3
      tasks:
      - name: t2  # Missing task.
      - name: t3
    - name: v4
      tasks:
      - name: t4  # Correct task list.
            """
        )

        violations = self.rule(self.good_config, bad_yaml)
        self.assertEqual(len(violations), 2)
