import unittest

from evergreen_lint import rules
from evergreen_lint.yamlhandler import load


class TestEnforceTagsForTasks(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = rules.enforce_tags_for_tasks.EnforceTagsForTasks()

    def test_tag_presence_is_enforced(self):
        rule_config = {
            "tag_groups": [
                {
                    "group_name": "tag_group_name",
                    "tag_regex": "required_tag_.+",
                    "tag_list": [
                        "required_tag_test_1",
                        "required_tag_test_2",
                    ],
                    "min_num_of_tags": 1,
                    "max_num_of_tags": 1,
                }
            ]
        }

        yaml = load(
            """
            tasks:
            - name: t1
              tags: ["required_tag_test_1"]
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 0)

    def test_duplicated_tags_in_yaml_are_treated_as_single_tag(self):
        rule_config = {
            "tag_groups": [
                {
                    "group_name": "tag_group_name",
                    "tag_regex": "required_tag_.+",
                    "tag_list": [
                        "required_tag_test_1",
                        "required_tag_test_2",
                    ],
                    "min_num_of_tags": 1,
                    "max_num_of_tags": 1,
                }
            ]
        }

        yaml = load(
            """
            tasks:
            - name: t1
              tags: ["required_tag_test_1", "required_tag_test_1"]
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 0)

    def test_tag_list_is_violated(self):
        rule_config = {
            "tag_groups": [
                {
                    "group_name": "tag_group_name",
                    "tag_regex": "required_tag_.+",
                    "tag_list": [
                        "required_tag_test_1",
                        "required_tag_test_2",
                    ],
                }
            ]
        }

        yaml = load(
            """
            tasks:
            - name: t1
              tags: ["required_tag_test"]
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 1)

    def test_tag_list_and_num_of_tags_are_violated(self):
        rule_config = {
            "tag_groups": [
                {
                    "group_name": "tag_group_name",
                    "tag_regex": "required_tag_.+",
                    "tag_list": [
                        "required_tag_test_1",
                        "required_tag_test_2",
                    ],
                    "min_num_of_tags": 1,
                    "max_num_of_tags": 1,
                }
            ]
        }

        yaml = load(
            """
            tasks:
            - name: t1
              tags: ["required_tag_test"]
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 2)

    def test_min_num_of_tags_is_violated_when_tags_key_present_in_yaml(self):
        rule_config = {
            "tag_groups": [
                {
                    "group_name": "tag_group_name",
                    "tag_list": [
                        "required_tag_test_1",
                        "required_tag_test_2",
                    ],
                    "min_num_of_tags": 1,
                    "max_num_of_tags": 1,
                }
            ]
        }

        yaml = load(
            """
            tasks:
            - name: t1
              tags: []
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 1)

    def test_min_num_of_tags_is_violated_when_tags_key_absent_in_yaml(self):
        rule_config = {
            "tag_groups": [
                {
                    "group_name": "tag_group_name",
                    "tag_list": [
                        "required_tag_test_1",
                        "required_tag_test_2",
                    ],
                    "min_num_of_tags": 1,
                    "max_num_of_tags": 1,
                }
            ]
        }

        yaml = load(
            """
            tasks:
            - name: t1
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 1)

    def test_max_num_of_tags_is_violated(self):
        rule_config = {
            "tag_groups": [
                {
                    "group_name": "tag_group_name",
                    "tag_list": [
                        "required_tag_test_1",
                        "required_tag_test_2",
                    ],
                    "min_num_of_tags": 1,
                    "max_num_of_tags": 1,
                }
            ]
        }

        yaml = load(
            """
            tasks:
            - name: t1
              tags: ["required_tag_test_1", "required_tag_test_2"]
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 1)
