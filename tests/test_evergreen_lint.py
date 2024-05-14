import yaml

from evergreen_lint import __version__
from evergreen_lint.config import STUB
from evergreen_lint.config import load as load_config
from evergreen_lint.rules import RULES


def test_version():
    assert __version__ == "0.1.7"


def test_stub_formatting():
    # i'm picky. I don't want leading newlines from this when printed, so
    # STUB must not start or end with a \n. The print() command will add
    # a trailing newline, yielding the output I want
    assert STUB[0] != "\n"
    assert STUB[-1] != "\n"


def test_stub_for_every_rule():
    # stub must contain an entry for each rule

    config = yaml.safe_load(STUB)
    rules = set()
    for rule_name in config["rules"]:
        rules.add(rule_name["rule"])

    rules_defined = set()
    for rule_name in RULES.keys():
        rules_defined.add(rule_name)

    assert rules_defined ^ rules == set()

    # while we're here, assert that the defaults in code match the defaults
    # in the stub
    for rule in config["rules"]:
        rule_cpy = dict(rule)
        del rule_cpy["rule"]
        assert RULES[rule["rule"]].defaults() == rule_cpy
    for rule_name, rulecls in RULES.items():
        assert rulecls.name() == rule_name


def test_stub_is_valid():
    config = load_config(STUB, "/test")
    # fn throws if there is an error
    assert config["files"][0] == "/test/evergreen.yml"
