from __future__ import annotations

from typing import List, Dict, Set

from evergreen_lint.model import LintError, Rule


class PreventExperimentalTasksInNonExperimentalVariants(Rule):
    """
    Prevent experimental tasks from being used in non-experimental buildvariants.

    This rule checks that:
    1. Tasks with the "experimental" tag are not used in buildvariants with the "no_task_tag_experimental" tag.
    2. Ignores specified tasks even if they are experimental and in non-experimental buildvariants.
    """

    @staticmethod
    def name() -> str:
        return "prevent-experimental-tasks-in-non-experimental-variants"

    @staticmethod
    def defaults() -> dict:
        return {
            "task_experimental_tag": "experimental",
            "variant_no_experimental_tag": "no_task_tag_experimental",
            "ignored_tasks": []
        }

    @staticmethod
    def _get_variant_tasks(variant: Dict) -> Set[str]:
        return {task['name'] for task in variant.get('tasks', [])}

    def __call__(self, config: dict, yaml: dict) -> List[LintError]:
        failed_checks = []

        task_experimental_tag = config.get("task_experimental_tag", "experimental")
        variant_no_experimental_tag = config.get("variant_no_experimental_tag", "no_task_tag_experimental")
        ignored_tasks = set(config.get("ignored_tasks", []))

        # Find all experimental tasks
        experimental_tasks: Set[str] = set()
        for task in yaml.get("tasks", []):
            if task_experimental_tag in task.get("tags", []):
                experimental_tasks.add(task["name"])

        # Check buildvariants
        for variant in yaml.get("buildvariants", []):
            variant_name = variant["name"]
            variant_tags = set(variant.get("tags", []))
            
            if variant_no_experimental_tag not in variant_tags:
                continue

            variant_tasks = self._get_variant_tasks(variant)

            for task_name in variant_tasks:
                if task_name in experimental_tasks and task_name not in ignored_tasks:
                    failed_checks.append(
                        f"Experimental task '{task_name}' is used in buildvariant '{variant_name}' "
                        f"which is tagged as '{variant_no_experimental_tag}'.\n"
                    )
        return failed_checks
