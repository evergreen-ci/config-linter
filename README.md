# evergreen-lint

A linter for evergreen yamls.

Add to your requirements.txt as `evergreen-lint` (poetry: `poetry add -D evergreen-lint`)

Generate a stub configuration:
```
python -m evergreen_lint stub > evergreen_lint.yml
```

Edit the configuration stub to your liking.

Run with `python -m evergreen_lint -c evergreen_lint.yml lint`.


## Automatic Fixing
Not a feature :(. This is just a linter, i.e. it tells you what is wrong, but it
doesn't fix the errors for you.

Here's a handy guide to the errors, and how to fix them

### limit-keyval-inc
keyval.inc is a deprecated Evergreen command used by mongodb-mongo-master for
legacy purposes only. This rule indicates

### shell-exec-explicit-shell
A common Evergreen footgun is using shell.exec without specifying a shell. By
default, Evergreen uses /bin/sh, which is bash on every Linux distribution
except for Ubuntu, which a Dash. Dash is strictly a bourne compatible shell,
i.e. it doesn't implement bash-isms and other features that you expect.

*Solution*: Specify a shell. If you're not sure which shell, specify bash.

### no-working-dir-on-shell
This rule disables the working_dir parameter on shell.exec and subprocess.exec.

*Solution*: Perform cd in your shell script.

### invalid-function-name
Enforce consistent naming of Evergreen YAML functions. Note that in the
following example:
```
functions:
"f_my_func": &doesnt_match_rule
```
The function name is "f_my_func", not "doesnt_match_rule". There is no rule
for linting the yaml anchor ('doesnt_match_rule').

*Solution*: Make the function name match the given regex.

### invalid-build-parameter
Enforce consistent naming of build parameters.

*Solution*: Make the build parameter name match the given regex, and specify
a non-empty description.

### no-shell-exec
Forbid the use of shell.exec in the YAML.

*Solution*: Use subprocess.exec. Expansions can be made available as
environment variables by specifying `add_expansions_to_env: true` to the
params list.

### no-multiline-expansions.update
Forbid the use of multiline values to expansions.update.

*Solution*: Don't do that. If you absolutely must, see the `files` param in the
[documentation](https://github.com/evergreen-ci/evergreen/wiki/Project-Commands#expansions-update).

### dependency-for-func
Enforce that if a task contains a specified function, any dependencies required for
that function are included as dependencies of that task.

Since dependencies are defined at the task level, the dependency list provided in the
configuration takes funcs as the key and a list of task names as the value.

*Solution*: Add the required dependency to the task.

#### Configuration

Which dependencies should be enforced can be configured via the lint config files. The
configuration should use the following format:

```yaml
rules:
  - rule: dependency-for-func
    dependencies:
      func_name_0: [dependency_task_0, dependency_task_1]
      func_name_1:
        - dependency_task_2
```
