from __future__ import annotations

from typing import List, NamedTuple, Set

from evergreen_lint.model import LintError, Rule


class TagConfig(NamedTuple):
    variant_tag_name: str  # Tag name for the buildvariant
    prevent_task_tag: str  # Tag name for tasks that should be prevented
    ignored_tasks: List[str] = []  # List of task names to be ignored by this rule


class PreventTasksWithTagOnVariantsConfig(NamedTuple):
    tags: List[TagConfig]

    @classmethod
    def from_config_dict(cls, config_dict) -> PreventTasksWithTagOnVariantsConfig:
        return cls(tags=[TagConfig(**tag_config) for tag_config in config_dict.get("tags", [])])


class PreventTasksWithTagOnVariants(Rule):
    """
    Prevent tasks with specific tags from being used in buildvariants with certain tags.

    The configuration example:

    ```
    - rule: "prevent-tasks-with-tag-on-variants"
      tags:
        - variant_tag_name: "no_task_tag_experimental"
          prevent_task_tag: "experimental"
          ignored_tasks: []
        - variant_tag_name: "no_task_tag_release_critical"
          prevent_task_tag: "release_critical"
          ignored_tasks: []
    ```
    """

    @staticmethod
    def name() -> str:
        return "prevent-tasks-with-tag-on-variants"

    @staticmethod
    def defaults() -> dict:
        return {"tags": []}

    @staticmethod
    def _get_variant_tasks(variant: dict) -> Set[str]:
        # Extract task names from a variant
        return {task["name"] for task in variant.get("tasks", [])}

    def __call__(self, config: dict, yaml: dict) -> List[LintError]:
        failed_checks = []
        rule_config = PreventTasksWithTagOnVariantsConfig.from_config_dict(config)
        for tag_config in rule_config.tags:
            prevented_tasks: Set[str] = set()
            # Identify tasks with the prevented tag
            for task in yaml.get("tasks", []):
                if tag_config.prevent_task_tag in task.get("tags", []):
                    prevented_tasks.add(task["name"])

            # Check each buildvariant
            for variant in yaml.get("buildvariants", []):
                variant_name = variant["name"]
                variant_tags = set(variant.get("tags", []))

                if tag_config.variant_tag_name not in variant_tags:
                    continue

                variant_tasks = self._get_variant_tasks(variant)

                # Check each task in the variant
                for task_name in variant_tasks:
                    if task_name in prevented_tasks and task_name not in tag_config.ignored_tasks:
                        failed_checks.append(
                            f"Task '{task_name}' with tag '{tag_config.prevent_task_tag}' is used in buildvariant '{variant_name}' "
                            f"which is tagged as '{tag_config.variant_tag_name}'."
                        )

        return failed_checks
