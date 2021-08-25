from typing import List

from evergreen_lint.model import LintError, Rule


class TasksForVariantsConfig(object):
    def __init__(self, raw_mappings):
        self._raw_mappings = raw_mappings
        self._variant_mappings = {}
        self._unused_variants = set()

        for mapping in self._raw_mappings:
            tasks = set(mapping["tasks"])
            for variant in mapping["variants"]:
                # Each variant can only be defined with one set of tasks.
                if variant in self._variant_mappings:
                    raise ValueError(f"Invalid linter config: '{variant}' appeared more than once")
                self._variant_mappings[variant] = tasks
                self._unused_variants.add(variant)

    def tasks_for_variant(self, variant):

        res = self._variant_mappings.get(variant, None)
        if res is not None:
            self._unused_variants.remove(variant)
        return res

    def assert_no_unused_variants(self):
        if self._unused_variants:
            raise ValueError(
                f"Invalid linter config: unknown variant names: {self._unused_variants}"
            )


class TasksForVariants(Rule):

    """
    Enforce task definitions for variants.

    The configuration will look like:

    ```
    - rule: "tasks-for-variants"
      task-variant-mappings:
        - name: release-variants-tasks
          tasks:
          - task1
          - task2
          variants:
          - variant1
          - variant2
        - name: asan-variant-tasks
          tasks:
          - task1
          - task2
          - task3
          variants:
          - variant3
          - variant4
    ```

    """

    @staticmethod
    def name() -> str:
        return "tasks-for-variants"

    @staticmethod
    def defaults() -> dict:
        return {"task-variant-mappings": {}}

    @staticmethod
    def _get_task_set_from_list(task_list):
        return {task["name"] for task in task_list}

    def __call__(self, config: dict, yaml: dict) -> List[LintError]:
        error_msg = (
            "Mismatched task list for variant '{variant}'. Expected '{expected}', got '{actual}'"
        )

        failed_checks = []

        mappings = config.get("task-variant-mappings")
        config_wrapper = TasksForVariantsConfig(mappings)

        for variant_obj in yaml["buildvariants"]:
            variant = variant_obj["name"]
            expected_tasks = config_wrapper.tasks_for_variant(variant)
            actual_tasks = self._get_task_set_from_list(variant["tasks"])

            if expected_tasks != actual_tasks:
                failed_checks.append(
                    error_msg.format(variant=variant, expected=expected_tasks, actual=actual_tasks)
                )

        config_wrapper.assert_no_unused_variants()

        return failed_checks
