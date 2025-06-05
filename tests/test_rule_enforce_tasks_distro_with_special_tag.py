import unittest

from evergreen_lint import rules
from evergreen_lint.yamlhandler import load


class TestEnforceTasksDistroWithSpecialTag(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = rules.enforce_tasks_distro_with_special_tag.EnforceTasksDistroWithSpecialTag()
        self.rule_config = {
            "tags": [
                {
                    "task_tag_name": "requires_large_host",
                    "allowed_distro_regex": "(.*-xxlarge|.*-xlarge|.*-large|.*-medium|macos-.*)",
                }
            ]
        }

    def test_no_violations_when_tasks_on_correct_distros(self):
        yaml = load(
            """
            tasks:
            - name: task1
              tags: ["requires_large_host"]
            - name: task2
              tags: []
            buildvariants:
            - name: variant-1
              run_on:
                - rhel8-large
              tasks:
                - name: task1
                - name: task2
            """
        )

        violations = self.rule(self.rule_config, yaml)
        self.assertEqual(len(violations), 0)

    def test_violations_when_tasks_on_small_distros(self):
        yaml = load(
            """
            tasks:
            - name: task1
              tags: ["requires_large_host"]
            - name: task2
              tags: ["requires_large_host"]
            buildvariants:
            - name: variant-1
              run_on:
                - rhel8-small
              tasks:
                - name: task1
                - name: task2
            """
        )

        violations = self.rule(self.rule_config, yaml)
        self.assertEqual(len(violations), 2)
        self.assertIn("task1", violations[0])
        self.assertIn("rhel8-small", violations[0])
        self.assertIn("task2", violations[1])
        self.assertIn("rhel8-small", violations[1])

    def test_task_specific_run_on_overrides(self):
        yaml = load(
            """
            tasks:
            - name: task1
              tags: ["requires_large_host"]
            buildvariants:
            - name: variant-1
              run_on:
                - rhel8-small
              tasks:
                - name: task1
                  run_on:
                    - rhel8-large
            """
        )

        violations = self.rule(self.rule_config, yaml)
        self.assertEqual(len(violations), 0)

    def test_mixed_distro_configurations(self):
        yaml = load(
            """
            tasks:
            - name: task1
              tags: ["requires_large_host"]
            - name: task2
              tags: ["requires_large_host"]
            - name: task3
              tags: []
            buildvariants:
            - name: variant-1
              run_on:
                - rhel8.8-small
              tasks:
                - name: task1
                - name: task2
                  run_on:
                    - rhel8.8-large
                - name: task3
            """
        )

        violations = self.rule(self.rule_config, yaml)
        self.assertEqual(len(violations), 1)
        self.assertIn("task1", violations[0])
        self.assertIn("rhel8.8-small", violations[0])

    def test_mixed_distro_configurations1(self):
        yaml = load(
            """
            tasks:
            - name: task1
              tags: ["requires_large_host"]
            - name: task2
              tags: ["requires_large_host"]
            - name: task3
              tags: []
            buildvariants:
            - name: variant-1
              run_on:
                - rhel8.8-small
              tasks:
                - name: task1
                - name: task2
                  run_on:
                    - rhel8.8-large
                - name: task3
            """
        )

        violations = self.rule(self.rule_config, yaml)
        self.assertEqual(len(violations), 1)
        self.assertIn("task1", violations[0])
        self.assertIn("rhel8.8-small", violations[0])
