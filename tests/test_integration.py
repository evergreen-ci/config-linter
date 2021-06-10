from click.testing import CliRunner

import evergreen_lint.__main__ as ut


def test_good_run():
    runner = CliRunner()
    res = runner.invoke(ut.main, ["-c", "tests/yml/config.yml", "lint"])
    assert res.exit_code == 0


def test_with_errs():
    runner = CliRunner()
    res = runner.invoke(ut.main, ["-c", "tests/yml/config_with_errs.yml", "lint"])
    assert (
        "For help resolving errors, see the helpful documentation at "
        "https://github.com/evergreen-ci/config-lint"
    ) in res.output
    assert res.exit_code == 1


def test_with_errs_custom_url():
    runner = CliRunner()
    res = runner.invoke(ut.main, ["-c", "tests/yml/config_with_errs_custom.yml", "lint"])
    assert (
        "For help resolving errors, see the helpful documentation at http://example.com"
    ) in res.output
    assert res.exit_code == 1
