import pytest

from miras.cli import main


def test_help_and_version(capsys):
    import miras
    assert main([]) == 0
    assert main(["--version"]) == 0
    assert miras.__version__ in capsys.readouterr().out


def test_doctor(capsys):
    assert main(["doctor"]) == 0
    out = capsys.readouterr().out
    assert "numpy" in out and "daftar" in out and "CmdStan" in out


def test_unknown_command():
    assert main(["nope"]) == 2
    assert main(["paper", "nope"]) == 2
