import unittest

from evergreen_lint import rules
from evergreen_lint.yamlhandler import load


class TestEnforceTagsForVariants(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = rules.enforce_tags_for_variants.EnforceTagsForVariants()

    def test_tag_presence_is_enforced(self):
        rule_config = {
            "tags": [
                {
                    "tag_name": "required",
                    "variant_config": {
                        "name_regex": ".*",
                        "display_name_regex": "^! .+$",
                    },
                },
                {
                    "tag_name": "suggested",
                    "variant_config": {
                        "name_regex": ".*",
                        "display_name_regex": "^\\* .+$",
                    },
                },
            ]
        }

        yaml = load(
            """
            buildvariants:
            - name: variant-1
              display_name: "! Variant 1"
              tags: ["required"]
            - name: variant-2
              display_name: "* Variant 2"
              tags: ["suggested"]
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 0)

    def test_variant_is_missing_tag(self):
        rule_config = {
            "tags": [
                {
                    "tag_name": "required",
                    "variant_config": {
                        "name_regex": ".*",
                        "display_name_regex": "^! .+$",
                    },
                },
            ]
        }

        yaml = load(
            """
            buildvariants:
            - name: variant-1
              display_name: "! Variant 1"
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 1)

    def test_variant_name_is_incorrect(self):
        rule_config = {
            "tags": [
                {
                    "tag_name": "required",
                    "variant_config": {
                        "name_regex": "^.*-suggested$",
                        "display_name_regex": "^! .+$",
                    },
                },
            ]
        }

        yaml = load(
            """
            buildvariants:
            - name: variant-1
              display_name: "! Variant 1"
              tags: ["required"]
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 1)

    def test_variant_display_name_is_incorrect(self):
        rule_config = {
            "tags": [
                {
                    "tag_name": "required",
                    "variant_config": {
                        "name_regex": ".*",
                        "display_name_regex": "^! .+$",
                    },
                },
            ]
        }

        yaml = load(
            """
            buildvariants:
            - name: variant-1
              display_name: "Variant 1"
              tags: ["required"]
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 1)

    def test_entire_variant_configuration_is_incorrect(self):
        rule_config = {
            "tags": [
                {
                    "tag_name": "required",
                    "variant_config": {
                        "name_regex": "^.*-suggested$",
                        "display_name_regex": "^! .+$",
                    },
                },
            ]
        }

        yaml = load(
            """
            buildvariants:
            - name: variant-1
              display_name: "Variant 1"
              tags: ["required"]
            """
        )

        violations = self.rule(rule_config, yaml)
        self.assertEqual(len(violations), 1)
