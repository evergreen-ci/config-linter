from click.testing import CliRunner
import evergreen_lint.__main__ as ut

def main():
    runner = CliRunner()
    runner.invoke(ut.main, ["-c", "config.yml", "lint"])
