import unittest

from evergreen_lint import rules
from evergreen_lint.yamlhandler import load


class TestVariantExpansions(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = rules.variant_expansions.VariantExpansions()
        self.yaml = load(
            """
            buildvariants:
            - name: existing-variant-name
              display_name: "Existing Variant Display Name"
              expansions:
                existing_expansion_1: existing expansion value 1
                existing_expansion_2: existing expansion value 2
              tasks:
              - name: existing_task_1
              - name: existing_task_2
            """
        )

    def test_required_expansion_is_present_minimal_config(self):
        rule_config = {
            "require_expansions": [{"expansion_name": "existing_expansion_1"}],
            "prohibit_expansions": None,
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 0)

    def test_required_expansion_is_absent_minimal_config(self):
        rule_config = {
            "require_expansions": [{"expansion_name": "non_existing_expansion"}],
            "prohibit_expansions": None,
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 1)

    def test_required_expansion_is_present_on_variant_with_name(self):
        rule_config = {
            "require_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "variant_config": {"name_regex": "existing-variant-name"},
                }
            ],
            "prohibit_expansions": None,
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 0)

    def test_required_expansion_is_absent_on_variant_with_name(self):
        rule_config = {
            "require_expansions": [
                {
                    "expansion_name": "non_existing_expansion",
                    "variant_config": {"name_regex": "existing-variant-name"},
                }
            ],
            "prohibit_expansions": None,
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 1)

    def test_required_expansion_is_present_on_variant_with_display_name(self):
        rule_config = {
            "require_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "variant_config": {"display_name_regex": "Existing Variant Display Name"},
                }
            ],
            "prohibit_expansions": None,
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 0)

    def test_required_expansion_is_absent_on_variant_with_display_name(self):
        rule_config = {
            "require_expansions": [
                {
                    "expansion_name": "non_existing_expansion",
                    "variant_config": {"display_name_regex": "Existing Variant Display Name"},
                }
            ],
            "prohibit_expansions": None,
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 1)

    def test_required_expansion_is_present_on_variant_when_task_present(self):
        rule_config = {
            "require_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "variant_config": {"task_presence_regex": "existing_task_1"},
                }
            ],
            "prohibit_expansions": None,
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 0)

    def test_required_expansion_is_absent_on_variant_when_task_present(self):
        rule_config = {
            "require_expansions": [
                {
                    "expansion_name": "non_existing_expansion",
                    "variant_config": {"task_presence_regex": "existing_task_1"},
                }
            ],
            "prohibit_expansions": None,
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 1)

    def test_required_expansion_is_present_on_variant_when_task_absent(self):
        rule_config = {
            "require_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "variant_config": {"task_absense_regex": "absent_task"},
                }
            ],
            "prohibit_expansions": None,
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 0)

    def test_required_expansion_is_absent_on_variant_when_task_absent(self):
        rule_config = {
            "require_expansions": [
                {
                    "expansion_name": "non_existing_expansion",
                    "variant_config": {"task_absense_regex": "absent_task"},
                }
            ],
            "prohibit_expansions": None,
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 1)

    def test_required_expansion_value_is_valid(self):
        rule_config = {
            "require_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "expansion_value_regex": "existing expansion value 1",
                }
            ],
            "prohibit_expansions": None,
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 0)

    def test_required_expansion_value_is_invalid(self):
        rule_config = {
            "require_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "expansion_value_regex": "invalid value",
                }
            ],
            "prohibit_expansions": None,
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 1)

    def test_required_expansion_value_is_valid_full_config(self):
        rule_config = {
            "require_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "expansion_value_regex": "existing expansion value 1",
                    "variant_config": {
                        "name_regex": "existing-variant-name",
                        "display_name_regex": "Existing Variant Display Name",
                        "task_presence_regex": "existing_task_1",
                        "task_absense_regex": "absent_task",
                    },
                }
            ],
            "prohibit_expansions": None,
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 0)

    def test_required_expansion_value_is_invalid_full_config(self):
        rule_config = {
            "require_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "expansion_value_regex": "invalid value",
                    "variant_config": {
                        "name_regex": "existing-variant-name",
                        "display_name_regex": "Existing Variant Display Name",
                        "task_presence_regex": "existing_task_1",
                        "task_absense_regex": "absent_task",
                    },
                }
            ],
            "prohibit_expansions": None,
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 1)

    def test_prohibited_expansion_is_present_minimal_config(self):
        rule_config = {
            "require_expansions": None,
            "prohibit_expansions": [{"expansion_name": "existing_expansion_1"}],
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 1)

    def test_prohibited_expansion_is_absent_minimal_config(self):
        rule_config = {
            "require_expansions": None,
            "prohibit_expansions": [{"expansion_name": "non_existing_expansion"}],
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 0)

    def test_prohibited_expansion_is_present_on_variant_with_name(self):
        rule_config = {
            "require_expansions": None,
            "prohibit_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "variant_config": {"name_regex": "existing-variant-name"},
                }
            ],
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 1)

    def test_prohibited_expansion_is_absent_on_variant_with_name(self):
        rule_config = {
            "require_expansions": None,
            "prohibit_expansions": [
                {
                    "expansion_name": "non_existing_expansion",
                    "variant_config": {"name_regex": "existing-variant-name"},
                }
            ],
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 0)

    def test_prohibited_expansion_is_present_on_variant_with_display_name(self):
        rule_config = {
            "require_expansions": None,
            "prohibit_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "variant_config": {"display_name_regex": "Existing Variant Display Name"},
                }
            ],
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 1)

    def test_prohibited_expansion_is_absent_on_variant_with_display_name(self):
        rule_config = {
            "require_expansions": None,
            "prohibit_expansions": [
                {
                    "expansion_name": "non_existing_expansion",
                    "variant_config": {"display_name_regex": "Existing Variant Display Name"},
                }
            ],
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 0)

    def test_prohibited_expansion_is_present_on_variant_when_task_present(self):
        rule_config = {
            "require_expansions": None,
            "prohibit_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "variant_config": {"task_presence_regex": "existing_task_1"},
                }
            ],
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 1)

    def test_prohibited_expansion_is_absent_on_variant_when_task_present(self):
        rule_config = {
            "require_expansions": None,
            "prohibit_expansions": [
                {
                    "expansion_name": "non_existing_expansion",
                    "variant_config": {"task_presence_regex": "existing_task_1"},
                }
            ],
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 0)

    def test_prohibited_expansion_is_present_on_variant_when_task_absent(self):
        rule_config = {
            "require_expansions": None,
            "prohibit_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "variant_config": {"task_absense_regex": "absent_task"},
                }
            ],
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 1)

    def test_prohibited_expansion_is_absent_on_variant_when_task_absent(self):
        rule_config = {
            "require_expansions": None,
            "prohibit_expansions": [
                {
                    "expansion_name": "non_existing_expansion",
                    "variant_config": {"task_absense_regex": "absent_task"},
                }
            ],
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 0)

    def test_prohibited_expansion_with_matching_value(self):
        rule_config = {
            "require_expansions": None,
            "prohibit_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "expansion_value_regex": "existing expansion value 1",
                }
            ],
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 1)

    def test_prohibited_expansion_with_non_matching_value(self):
        rule_config = {
            "require_expansions": None,
            "prohibit_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "expansion_value_regex": "invalid value",
                }
            ],
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 0)

    def test_prohibited_expansion_with_matching_value_full_config(self):
        rule_config = {
            "require_expansions": None,
            "prohibit_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "expansion_value_regex": "existing expansion value 1",
                    "variant_config": {
                        "name_regex": "existing-variant-name",
                        "display_name_regex": "Existing Variant Display Name",
                        "task_presence_regex": "existing_task_1",
                        "task_absense_regex": "absent_task",
                    },
                }
            ],
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 1)

    def test_prohibited_expansion_with_non_matching_value_full_config(self):
        rule_config = {
            "require_expansions": None,
            "prohibit_expansions": [
                {
                    "expansion_name": "existing_expansion_1",
                    "expansion_value_regex": "invalid value",
                    "variant_config": {
                        "name_regex": "existing-variant-name",
                        "display_name_regex": "Existing Variant Display Name",
                        "task_presence_regex": "existing_task_1",
                        "task_absense_regex": "absent_task",
                    },
                }
            ],
        }

        violations = self.rule(rule_config, self.yaml)
        self.assertEqual(len(violations), 0)
