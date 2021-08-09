"""Lint rules."""
import re
from typing import Dict, List, Optional, Set, Type

import evergreen_lint.helpers as helpers
from evergreen_lint.helpers import (
    determine_dependencies_of_task_def,
    iterate_command_lists,
    iterate_commands,
    iterate_fn_calls_context,
)
from evergreen_lint.model import LintError, Rule


class LimitKeyvalInc(Rule):
    """Prevent/Limit usage of keyval.inc."""

    @staticmethod
    def name() -> str:
        return "limit-keyval-inc"

    @staticmethod
    def defaults() -> dict:
        return {"limit": 0}

    def __call__(self, config: dict, yaml: dict) -> List[LintError]:
        def _out_message(context: str) -> LintError:
            return (
                f"{context} uses keyval.inc. The entire file must not use "
                f"keyval.inc more than {config['limit']} times."
            )

        out: List[LintError] = []
        count = 0
        for context, command in iterate_commands(yaml):
            if "command" in command and command["command"] == "keyval.inc":
                out.append(_out_message(context))
                count += 1

        if count <= config["limit"]:
            return []
        return out


class ShellExecExplicitShell(Rule):
    """Require explicitly specifying shell in uses of shell.exec."""

    @staticmethod
    def name() -> str:
        return "shell-exec-explicit-shell"

    @staticmethod
    def defaults() -> dict:
        return {}

    def __call__(self, config: dict, yaml: dict) -> List[LintError]:
        def _out_message(context: str) -> LintError:
            return (
                f"{context} is a shell.exec command without an explicitly "
                "declared shell. You almost certainly want to add 'shell: "
                "bash' to the parameters list."
            )

        out: List[LintError] = []
        for context, command in iterate_commands(yaml):
            if "command" in command and command["command"] == "shell.exec":
                if "params" not in command or "shell" not in command["params"]:
                    out.append(_out_message(context))

        return out


SHELL_COMMANDS = ["subprocess.exec", "subprocess.scripting", "shell.exec"]


class NoWorkingDirOnShell(Rule):
    """Do not allow working_dir to be set on shell.exec, subprocess.*."""

    @staticmethod
    def name() -> str:
        return "no-working-dir-on-shell"

    @staticmethod
    def defaults() -> dict:
        return {}

    def __call__(self, config: dict, yaml: dict) -> List[LintError]:
        def _out_message(context: str, cmd: str) -> LintError:
            return (
                f"{context} is a {cmd} command with a working_dir "
                "parameter. Do not set working_dir, instead `cd` into the "
                "directory in the shell script."
            )

        out: List[LintError] = []
        for context, command in iterate_commands(yaml):
            if "command" in command and command["command"] in SHELL_COMMANDS:
                if "params" in command and "working_dir" in command["params"]:
                    out.append(_out_message(context, command["command"]))

        return out


class InvalidFunctionName(Rule):
    """Enforce naming convention on functions."""

    @staticmethod
    def name() -> str:
        return "invalid-function-name"

    @staticmethod
    def defaults() -> dict:
        return {"regex": "^f_[a-z][A-Za-z0-9_]*"}

    def __call__(self, config: dict, yaml: dict) -> List[LintError]:
        FUNCTION_NAME = config["regex"]
        FUNCTION_NAME_RE = re.compile(FUNCTION_NAME)

        def _out_message(context: str) -> LintError:
            return f"Function '{context}' must have a name matching '{FUNCTION_NAME}'"

        if "functions" not in yaml:
            return []

        out: List[LintError] = []
        for fname in yaml["functions"].keys():
            if not FUNCTION_NAME_RE.fullmatch(fname):
                out.append(_out_message(fname))

        return out


class NoShellExec(Rule):
    """Do not allow shell.exec. Users should use subprocess.exec instead."""

    @staticmethod
    def name() -> str:
        return "no-shell-exec"

    @staticmethod
    def defaults() -> dict:
        return {}

    def __call__(self, config: dict, yaml: dict) -> List[LintError]:
        def _out_message(context: str) -> LintError:
            return (
                f"{context} is a shell.exec command, which is forbidden. "
                "Extract your shell script out of the YAML and into a .sh file "
                "in directory 'evergreen', and use subprocess.exec instead."
            )

        out: List[LintError] = []
        for context, command in iterate_commands(yaml):
            if "command" in command and command["command"] == "shell.exec":
                out.append(_out_message(context))
        return out


class NoMultilineExpansionsUpdate(Rule):
    @staticmethod
    def name() -> str:
        return "no-multiline-expansions-update"

    @staticmethod
    def defaults() -> dict:
        return {}

    def __call__(self, config: dict, yaml: dict) -> List[LintError]:
        """Forbid multi-line values in expansion.updates parameters."""

        def _out_message(context: str, idx: int) -> LintError:
            return (
                f"{context}, key-value pair {idx} is an expansions.update "
                "command with multi-line values embedded in the yaml, which is"
                " forbidden. For long-form values, use the files parameter of "
                "expansions.update."
            )

        out: List[LintError] = []
        for context, command in iterate_commands(yaml):
            if "command" in command and command["command"] == "expansions.update":
                if "params" in command and "updates" in command["params"]:
                    for idx, item in enumerate(command["params"]["updates"]):
                        if "value" in item and "\n" in item["value"]:
                            out.append(_out_message(context, idx))
        return out


class InvalidBuildParameter(Rule):
    """Require that parameters obey a naming convention and have a description."""

    @staticmethod
    def name() -> str:
        return "invalid-build-parameter"

    @staticmethod
    def defaults() -> dict:
        return {"regex": "[a-z][a-z0-9_]*", "require-description": True}

    def __call__(self, config: dict, yaml: dict) -> List[LintError]:
        BUILD_PARAMETER = config["regex"]
        BUILD_PARAMETER_RE = re.compile(BUILD_PARAMETER)

        def _out_message_key(idx: int) -> LintError:
            return f"Build parameter, pair {idx}, key must match '{BUILD_PARAMETER}'."

        def _out_message_description(idx: int) -> LintError:
            return f"Build parameter, pair {idx}, must have a description."

        if "parameters" not in yaml:
            return []

        out: List[LintError] = []
        for idx, param in enumerate(yaml["parameters"]):
            if "key" not in param or not BUILD_PARAMETER_RE.fullmatch(param["key"]):
                out.append(_out_message_key(idx))
            if (
                config["require-description"]
                and "description" not in param
                or not param["description"]
            ):
                out.append(_out_message_description(idx))
        return out


class RequiredExpansionsWrite(Rule):
    """Require that subprocess.exec functions that consume evergreen scripts
    correctly bootstrap the prelude."""

    @staticmethod
    def name() -> str:
        return "required-expansions-write"

    @staticmethod
    def defaults() -> dict:
        return {"regex": ".*\\/evergreen\\/.*\\.sh"}

    # pylint: disable=too-many-branches,too-many-locals,too-many-statements
    def __call__(self, config: dict, yaml: dict) -> List[LintError]:

        # This logic is well and truly awful.
        # Here's the problem:
        # 1. Evergreen functions can have a dict or list definition. Functions
        # with a dict definition, that is:
        #   "f_my_fn": &f_my_fn
        #     command: shell.exec
        # can called either as "- func: f_my_fn" or as *f_my_fn. The former syntax
        # can have arguments passed into it. The latter syntax,
        # i.e. the use of the YAML anchor, is used to workaround Evergreen not
        # allowing functions to call other functions. Arguments cannot be passed in
        # when the YAML anchor syntax is used.

        # This poses a problem: if the user calls a function with a dict definition,
        # and that function has arguments passed in, and that function calls
        # subprocess.exec, then the function will not have its expansions populated
        # in the external script as expected. It must be defined as a list, and
        # incorporate an expansions.write call, or not be called with args.
        # See Resolution 1.

        # Functions with a list definition, that is:
        #   "f_my_fn2": &f_my_fn2
        #     - command: shell.exec
        #     - command: shell.exec
        # cannot use the YAML anchor syntax (this is an evergreen validation
        # error). If these functions call subprocess.exec, then they will only work
        # if expansions.write is called before subprocess.exec. See Resolution 2.
        #
        # 2. Expansions can be defined/changed at any step of the way by Evergreen,
        # function arguments, build variants, Evergreen projects, tasks. Expansions
        # written to disk MUST be up to date. See Resolution 2
        # 3. Expansions be updated after expansions.update, but before
        # subprocess.exec. See Resolution 3.

        # Resolutions:
        # Given the above, here are the checks we need to perform
        # 1. Any function defined with a dict definition that calls subprocess.exec
        # MUST NOT be called with arguments.
        # 2. expansions.write MUST be called prior to invoking subprocess.exec for
        # the first time in any command list.
        # (i.e. in tasks: commands, setup_task, setup_group, teardown_task,
        # teardown_group, timeout,, globally: pre, post, timeout, functions with
        # list definitions)
        # When paired with Resolution 3, this works all the time (but does
        # sometimes require redundant expansions.write calls)
        # 3. Every invocation of expansions.update MUST be immediately followed by
        # expansions.write

        # 4. It makes sense to place your expansions.write call in a dict
        # definition function, that way you can call it with either syntax. So, in
        # the above passage where I've mentioned "expansions.write", we must not
        # only check for a properly formed expansions.write call, we must also
        # check for a function that calls expansions.write. For reference, a
        # properly formed expansions.write call looks like this:
        #   command: expansions.write
        #   params:
        #     file: expansions.yml
        #     redacted: true
        # A function containing the above as a dict definition is treated as
        # equivalent to calling expansions.write
        #
        # 5. Furthermore, above mentions of subprocess.exec MUST be applied only to
        # subprocess.exec invocations that call scripts in the evergreen directory.
        #
        # 6. And because that's not complicated enough, any functions that are
        # dict-defined with subprocess.exec must be treated as equivalent to
        # subprocess.exec on its own.
        # 7. Functions that call expansions.update, and are dict-defined MUST
        # require an expansions.update call after they are called, regardless of
        # syntax
        # 8. timeout.update can also affect expansion values, and all of the rules
        # above need to applied equally to timeout.update

        # These are functions that invoke expansions.write in a dict defintion,
        # as described in Resolution 4.
        expansions_write_fns: Set[str] = set()
        # These are functions whose invocations must be checked for Resolution 1.
        subprocess_exec_fns: Set[str] = set()
        # And these are for Resolution 7
        expansions_update_fns: Set[str] = set()
        # and Resolution 8
        timeout_update_fns: Set[str] = set()

        def _out_message_dangerous_function(context: str) -> LintError:
            return f"{context} cannot safely take arguments. Call expansions.write with params: file: expansions.yml; redacted: true, (or use one of these functions: {list(expansions_write_fns)}) in the function, or do not pass arguments to it."  # noqa: E501

        def _out_message_expansions_update(
            context: str, fname: str = "expansions.update"
        ) -> LintError:
            return f"{context} is an {fname} command that is not immediately followed by an expansions.write call. Always call expansions.write with params: file: expansions.yml; redacted: true, (or use one of these functions: {list(expansions_write_fns)}) after calling {fname}."  # noqa: E501

        def _out_message_subprocess(context: str) -> LintError:
            return f"{context} calls an evergreen shell script without a preceding expansions.write call. Always call expansions.write with params: file: expansions.yml; redacted: true, (or use one of these functions: {list(expansions_write_fns)}) before calling an evergreen shell script via subprocess.exec."  # noqa: E501

        def _is_expansions_write_or_fn(command: dict) -> bool:
            return helpers.match_expansions_write(command) or (
                "func" in command and command["func"] in expansions_write_fns
            )

        def _is_subprocess_exec_or_fn(command: dict) -> bool:
            return helpers.match_subprocess_exec(command) or (
                "func" in command and command["func"] in subprocess_exec_fns
            )

        def _is_expansions_update_or_fn(command: dict) -> bool:
            return helpers.match_expansions_update(command) or (
                "func" in command and command["func"] in expansions_update_fns
            )

        def _is_timeout_update_or_fn(command: dict) -> bool:
            return helpers.match_timeout_update(command) or (
                "func" in command and command["func"] in timeout_update_fns
            )

        def _context_add_fn(context: str, command: Optional[dict]) -> str:
            if command and "func" in command:
                return f'{context}, (function call: {command["func"]})'

            return context

        def _check_command_list(context: str, commands: List[dict]) -> List[LintError]:
            out: List[LintError] = []
            first_subprocess: Optional[int] = None
            first_subprocess_cmd: Optional[dict] = None
            first_exp_write: Optional[int] = None
            warned_subprocess = False
            for idx, command in enumerate(commands):
                if first_subprocess is None and _is_subprocess_exec_or_fn(command):
                    first_subprocess = idx
                    first_subprocess_cmd = command

                elif first_exp_write is None and _is_expansions_write_or_fn(command):
                    first_exp_write = idx

                if (
                    not warned_subprocess
                    and _is_subprocess_exec_or_fn(command)
                    and first_exp_write is None
                ):
                    out.append(
                        _out_message_subprocess(
                            _context_add_fn(f"{context}, command {idx}", command)
                        )
                    )
                    # only warn for the first instance of this per command list.
                    # Once you resolve the first instance, the Resolution 3 and
                    # Resolution 8 checks below handle the rest of the errors.
                    warned_subprocess = True

                if _is_expansions_update_or_fn(command) or _is_timeout_update_or_fn(command):
                    # Resolution 3 and Resolution 8
                    if len(commands) <= idx + 1 or not _is_expansions_write_or_fn(
                        commands[idx + 1]
                    ):
                        if _is_expansions_update_or_fn(command):
                            out.append(
                                _out_message_expansions_update(
                                    _context_add_fn(f"{context}, command {idx}", command)
                                )
                            )
                        elif _is_timeout_update_or_fn(command):
                            out.append(
                                _out_message_expansions_update(
                                    _context_add_fn(f"{context}, command {idx}", command),
                                    "timeout.update",
                                )
                            )

            if (
                not warned_subprocess
                and first_subprocess is not None
                and first_exp_write is not None
                and first_subprocess < first_exp_write
            ):
                out.append(
                    _out_message_subprocess(
                        _context_add_fn(
                            f"{context}, command {first_subprocess}", first_subprocess_cmd
                        )
                    )
                )

            return out

        out: List[LintError] = []
        if "functions" in yaml:
            for fname, body in yaml["functions"].items():
                if isinstance(body, dict):
                    # assemble the list of functions whose bodies are the expected
                    # expansions.write call. (Resolution 4)
                    if helpers.match_expansions_write(body):
                        expansions_write_fns.add(fname)
                    # assemble the list of functions that must never be called
                    # with arguments (Resolution 1)
                    elif helpers.match_subprocess_exec(body):
                        subprocess_exec_fns.add(fname)
                    # Resolution 7
                    elif helpers.match_expansions_update(body):
                        expansions_update_fns.add(fname)
                    # Resolution 8
                    elif helpers.match_timeout_update(body):
                        timeout_update_fns.add(fname)

        for context, commands in iterate_command_lists(yaml):
            if isinstance(commands, dict):
                continue
            out += _check_command_list(context, commands)

        for context, command, _ in iterate_fn_calls_context(yaml):
            if command["func"] in subprocess_exec_fns and "vars" in command and command["vars"]:
                out.append(_out_message_dangerous_function(context))

        return out


class DependencyForFunc(Rule):
    """
    Define dependencies that are required if a function is used.

    The configuration will look like:

    ```
    - rule: "dependency-for-func"
      dependencies:
        func_name: [dependency_0, depdendency_1]
    ```

    """

    @staticmethod
    def name() -> str:
        return "dependency-for-func"

    @staticmethod
    def defaults() -> dict:
        return {"dependencies": {}}

    def __call__(self, config: dict, yaml: dict) -> List[LintError]:
        error_msg = (
            "Missing dependency. The task '{task_name}' expects '{dependency}' to be "
            "listed as a dependency due to the use of the '{function}' func."
        )
        failed_checks = []
        dependency_map = config.get("dependencies", {})
        for task_def in yaml.get("tasks"):
            actual_dependencies = determine_dependencies_of_task_def(task_def)
            funcs = [cmd["func"] for cmd in task_def.get("commands", []) if "func" in cmd]
            for func in funcs:
                expected_dependencies = dependency_map.get(func, [])
                unmet_dependenices = [
                    dep for dep in expected_dependencies if dep not in actual_dependencies
                ]
                failed_checks.extend(
                    [
                        error_msg.format(task_name=task_def["name"], dependency=dep, function=func)
                        for dep in unmet_dependenices
                    ]
                )

        return failed_checks


RULES: Dict[str, Type[Rule]] = {
    "limit-keyval-inc": LimitKeyvalInc,
    "shell-exec-explicit-shell": ShellExecExplicitShell,
    "no-working-dir-on-shell": NoWorkingDirOnShell,
    "invalid-function-name": InvalidFunctionName,
    "no-shell-exec": NoShellExec,
    "no-multiline-expansions-update": NoMultilineExpansionsUpdate,
    "invalid-build-parameter": InvalidBuildParameter,
    "required-expansions-write": RequiredExpansionsWrite,
    "dependency-for-func": DependencyForFunc,
}
# Thoughts on Writing Rules
# - see .helpers for reliable iteration helpers
# - Do not assume a key exists, unless it's been mentioned here
# - Do not allow exceptions to percolate outside of the rule function
# - YAML anchors are not available. Unless you want to write your own yaml
#   parser, or fork adrienverge/yamllint, abandon all hope on that idea you have.
# - Anchors are basically copy and paste, so you might see "duplicate" errors
#   that originate from the same anchor, but are reported in multiple locations

# Evergreen YAML Root Structure Reference
# Unless otherwise mentioned, the key is optional. You can infer the
# substructure by reading etc/evergreen.yml

# Function blocks: are dicts with the key 'func', which maps to a string,
# the name of the function
# Command blocks: are dicts with the key 'command', which maps to a string,
# the Evergreen command to run

# variables: List[dict]. These can be any valid yaml and it's very difficult
#   to infer anything
# functions: Dict[str, Union[dict, List[dict]]]. The key is the name of the
#   function, the value is either a dict, or list of dicts, with each dict
#   representing a command
# pre, post, and timeout: List[dict] representing commands or functions to
#   be run before/after/on timeout condition respectively
# tasks: List[dict], each dict is a task definition, key is always present
# task_groups: List[dict]
# modules: List[dict]
# buildvariants: List[dict], key is always present
# parameters: List[dict]
