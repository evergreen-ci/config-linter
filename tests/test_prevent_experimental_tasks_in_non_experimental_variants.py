import unittest


from evergreen_lint import rules
from evergreen_lint.yamlhandler import load


class TestPreventExperimentalTasksInNonExperimentalVariants(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = rules.prevent_experimental_tasks_in_non_experimental_variants.PreventExperimentalTasksInNonExperimentalVariants()

    def test_no_violations_when_experimental_tasks_in_appropriate_variants(self):
        rule_config = {
            "task_experimental_tag": "experimental",
            "variant_no_experimental_tag": "no_task_tag_experimental"
        }

        yaml = load(
            """
            tasks:
            - name: task1
              tags: ["experimental"]
            - name: task2
              tags: []
            buildvariants:
            - name: variant-1
              tasks: 
                - name: task2
            - name: variant-2
              tags: ["suggested"]
              tasks:
                - name: task1
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 0)

    def test_violation_when_experimental_task_in_non_experimental_variant(self):
        rule_config = {
            "task_experimental_tag": "experimental",
            "variant_no_experimental_tag": "no_task_tag_experimental"
        }

        yaml = load(
            """
            tasks:
              - name: task1
                tags: ["experimental"]
              - name: task2
                tags: []
            buildvariants:
              - name: variant-1
                tags: ["no_task_tag_experimental"]
                tasks:
                  - name: task1
                  - name: task2
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 1)
        self.assertIn("variant-1", violations[0])
        self.assertIn("task1", violations[0])

    def test_multiple_violations_across_different_variants(self):
        rule_config = {
            "task_experimental_tag": "experimental",
            "variant_no_experimental_tag": "no_task_tag_experimental"
        }

        yaml = load(
            """
            tasks:
            - name: task1
              tags: ["experimental"]
            - name: task2
              tags: ["experimental"]
            - name: task3
              tags: []
            buildvariants:
            - name: variant-1
              tags: ["no_task_tag_experimental"]
              tasks: 
                - name: task1
                - name: task3
            - name: variant-2
              tags: ["no_task_tag_experimental"]
              tasks:
                - name: task2
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 2)
        self.assertIn("variant-1", violations[0])
        self.assertIn("task1", violations[0])
        self.assertIn("variant-2", violations[1])
        self.assertIn("task2", violations[1])

    def test_ignored_tasks_are_not_reported_as_violations(self):
        rule_config = {
            "task_experimental_tag": "experimental",
            "variant_no_experimental_tag": "no_task_tag_experimental",
            "ignored_tasks": ["special_task"]
        }

        yaml = load(
            """
            tasks:
            - name: task1
              tags: ["experimental"]
            - name: special_task
              tags: ["experimental"]
            buildvariants:
            - name: variant-1
              tags: ["no_task_tag_experimental"]
              tasks: 
                - name: task1
                - name: special_task
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 1)
        self.assertIn("task1", violations[0])
        self.assertNotIn("special_task", violations[0])
